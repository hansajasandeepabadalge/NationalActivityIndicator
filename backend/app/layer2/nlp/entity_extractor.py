import spacy
import re
import time
from typing import List
from dateutil import parser as date_parser
from app.layer2.nlp.entity_schemas import (
    Location, Organization, Person, DateEntity,
    AmountEntity, PercentageEntity, ExtractedEntities
)

class EntityExtractor:
    _instance = None
    _nlp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._nlp = spacy.load("en_core_web_sm")
        return cls._instance

    CURRENCY_PATTERN = re.compile(
        r'(?:Rs\.?|LKR|USD|\$)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|mn|bn)?',
        re.IGNORECASE
    )
    PERCENTAGE_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*%')

    def extract_entities(self, article_id: str, title: str, content: str) -> ExtractedEntities:
        """Extract all entities from article"""
        start_time = time.time()

        # 50k chars keeps spaCy en_core_web_sm well within memory limits
        full_text = f"{title}\n\n{content}"[:50_000]

        doc = self._nlp(full_text)

        locations = self._extract_locations(doc)
        organizations = self._extract_organizations(doc)
        persons = self._extract_persons(doc)
        dates = self._extract_dates(doc)

        # Extract amounts: spaCy MONEY entities + regex (deduplicated)
        amounts = self._extract_amounts(full_text, doc)
        percentages = self._extract_percentages(full_text)

        processing_time = (time.time() - start_time) * 1000

        return ExtractedEntities(
            article_id=article_id,
            locations=locations,
            organizations=organizations,
            persons=persons,
            dates=dates,
            amounts=amounts,
            percentages=percentages,
            processing_time_ms=processing_time
        )

    def _extract_locations(self, doc) -> List[Location]:
        """Extract GPE and LOC entities"""
        locations = []
        seen = set()

        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                normalized = ent.text.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)
                    locations.append(Location(
                        text=ent.text,
                        start_char=ent.start_char,
                        end_char=ent.end_char
                    ))

        return locations

    def _extract_organizations(self, doc) -> List[Organization]:
        """Extract ORG entities"""
        orgs = []
        seen = set()

        for ent in doc.ents:
            if ent.label_ == "ORG":
                normalized = ent.text.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)
                    orgs.append(Organization(
                        text=ent.text,
                        start_char=ent.start_char,
                        end_char=ent.end_char
                    ))

        return orgs

    def _extract_persons(self, doc) -> List[Person]:
        """Extract PERSON entities"""
        persons = []
        seen = set()

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                normalized = ent.text.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)
                    persons.append(Person(
                        text=ent.text,
                        start_char=ent.start_char,
                        end_char=ent.end_char
                    ))

        return persons

    def _extract_dates(self, doc) -> List[DateEntity]:
        """Extract DATE entities with parsing"""
        dates = []
        seen = set()

        for ent in doc.ents:
            if ent.label_ == "DATE":
                normalized = ent.text.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)

                    parsed_date = None
                    try:
                        parsed_date = date_parser.parse(ent.text, fuzzy=True)
                    except Exception:
                        pass

                    dates.append(DateEntity(
                        text=ent.text,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        parsed_date=parsed_date
                    ))

        return dates

    def _extract_amounts(self, text: str, doc=None) -> List[AmountEntity]:
        """Extract currency amounts from spaCy MONEY entities and regex, deduplicated."""
        amounts = []
        seen_spans: set = set()  # (start_char, end_char) dedup

        def _add_amount(text_fragment: str, start: int, end: int) -> None:
            span_key = (start, end)
            if span_key in seen_spans:
                return
            seen_spans.add(span_key)
            try:
                currency_text = text_fragment
                if "USD" in currency_text or "$" in currency_text:
                    currency = "USD"
                else:
                    currency = "LKR"

                match = self.CURRENCY_PATTERN.search(currency_text)
                if not match:
                    return

                amount_str = match.group(1).replace(",", "")
                amount = float(amount_str)

                multiplier_text = match.group(2)
                if multiplier_text:
                    mult = multiplier_text.lower()
                    if mult in ["million", "mn"]:
                        amount *= 1_000_000
                    elif mult in ["billion", "bn"]:
                        amount *= 1_000_000_000

                amounts.append(AmountEntity(
                    text=text_fragment,
                    start_char=start,
                    end_char=end,
                    currency=currency,
                    amount=amount
                ))
            except Exception:
                pass

        # Pass 1: spaCy MONEY entities (blueprint §2.6 requirement)
        if doc is not None:
            for ent in doc.ents:
                if ent.label_ == "MONEY":
                    _add_amount(ent.text, ent.start_char, ent.end_char)

        # Pass 2: regex for currency patterns not caught by spaCy NER
        for match in self.CURRENCY_PATTERN.finditer(text):
            _add_amount(match.group(0), match.start(), match.end())

        return amounts

    def _extract_percentages(self, text: str) -> List[PercentageEntity]:
        """Extract percentage values using regex, deduplicated."""
        percentages = []
        seen_spans: set = set()

        for match in self.PERCENTAGE_PATTERN.finditer(text):
            span_key = (match.start(), match.end())
            if span_key in seen_spans:
                continue
            seen_spans.add(span_key)
            try:
                value = float(match.group(1))
                percentages.append(PercentageEntity(
                    text=match.group(0),
                    start_char=match.start(),
                    end_char=match.end(),
                    value=value
                ))
            except Exception:
                continue

        return percentages
