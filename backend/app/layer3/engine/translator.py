from typing import Dict, List, Any, Optional
import ast
import math
import operator as op

class ImpactTranslator:
    
    def __init__(self, translation_rules: List[Dict[str, Any]] = None, industry_templates: Dict[str, Any] = None):
        self.translation_rules = translation_rules or []
        self.industry_templates = industry_templates or {}
    
    def translate_to_operational(self, national_indicator: Dict[str, Any], company_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main translation function
        """
        
        national_code = national_indicator['indicator_code']
        national_value = national_indicator['current_value']
        industry = company_profile['industry']
        
        # Step 1: Check relevance
        is_relevant = self._check_relevance(national_code, industry, company_profile)
        
        if not is_relevant:
            return []
        
        # Step 2: Get industry sensitivity
        sensitivity = self._get_industry_sensitivity(national_code, industry)
        
        # Step 3: Get company-specific factors
        company_factor = self._get_company_factor(national_code, company_profile)
        
        # Step 4: Find applicable translation rules
        rules = self._find_translation_rules(national_code, industry)
        
        # Step 5: Apply translation
        operational_impacts = []
        
        for rule in rules:
            impact = self._apply_translation_rule(
                rule,
                national_value,
                sensitivity,
                company_factor
            )
            
            operational_impacts.append(impact)
        
        return operational_impacts
    
    def _check_relevance(self, national_code: str, industry: str, company_profile: Dict[str, Any]) -> bool:
        """
        Determine if this national indicator is relevant to this business
        """
        # Get industry template
        template = self.industry_templates.get(industry)
        
        if not template:
            # Fallback: if no template, assume relevant if rules exist
            return True
        
        # Check if national indicator is in sensitivity config
        sensitivities = template.get('sensitivity_config', {}).get('national_indicators', {})
        
        if national_code not in sensitivities:
            return False
        
        # Check relevance score
        relevance = sensitivities[national_code].get('relevance', 0)
        
        # Threshold: Only relevant if score > 0.3
        return relevance > 0.3
    
    def _get_industry_sensitivity(self, national_code: str, industry: str) -> Dict[str, float]:
        """
        Get how sensitive this industry is to this national indicator
        """
        template = self.industry_templates.get(industry, {})
        sensitivities = template.get('sensitivity_config', {}).get('national_indicators', {})
        
        indicator_sensitivity = sensitivities.get(national_code, {})
        
        return {
            'relevance': indicator_sensitivity.get('relevance', 0.5),
            'impact_multiplier': indicator_sensitivity.get('impact_multiplier', 1.0)
        }
    
    def _get_company_factor(self, national_code: str, company_profile: Dict[str, Any]) -> float:
        """
        Calculate company-specific adjustment factor
        """
        # Example: Fuel shortage impact depends on fuel dependency
        if 'FUEL' in national_code:
            dependency = company_profile.get('critical_dependencies', {}).get('fuel', 'medium')
            
            dependency_multipliers = {
                'critical': 1.5,
                'high': 1.2,
                'medium': 1.0,
                'low': 0.7
            }
            
            return dependency_multipliers.get(dependency, 1.0)
        
        # Example: Import-related indicators depend on import dependency
        if 'IMPORT' in national_code or 'CURRENCY' in national_code:
            import_dep = company_profile.get('supply_chain', {}).get('import_dependency', 0.5)
            
            # Higher import dependency = higher impact
            return 0.5 + (import_dep * 1.0)  # Range: 0.5 to 1.5
        
        # Default: No company-specific adjustment
        return 1.0
    
    def _find_translation_rules(self, national_code: str, industry: str) -> List[Dict[str, Any]]:
        """
        Find applicable translation rules
        """
        applicable_rules = []
        
        for rule in self.translation_rules:
            if rule['national_indicator_code'] == national_code:
                # Check if rule applies to this industry
                if (rule.get('applicable_industries') is None or
                    industry in rule['applicable_industries']):
                    applicable_rules.append(rule)
        
        return applicable_rules
    
    def _apply_translation_rule(self, rule: Dict[str, Any], national_value: float, sensitivity: Dict[str, float], company_factor: float) -> Dict[str, Any]:
        """
        Apply specific translation rule
        """
        rule_type = rule['rule_config']['type']
        
        if rule_type == 'linear':
            base_impact = national_value * sensitivity['impact_multiplier'] * company_factor
            operational_value = max(0, min(100, base_impact))
        
        elif rule_type == 'threshold':
            thresholds = rule['rule_config']['thresholds']
            operational_value = self._apply_threshold_rule(national_value, thresholds)
        
        elif rule_type == 'formula':
            expression = rule['rule_config']['expression']
            operational_value = self._evaluate_formula(expression, national_value, sensitivity, company_factor)
        
        else:
            operational_value = national_value  # Pass-through
        
        return {
            'operational_indicator_code': rule['operational_indicator_code'],
            'value': operational_value,
            'rule_type': rule_type,
            'confidence': rule.get('confidence_level', 0.8),
            'impact_lag_hours': rule.get('impact_lag_hours', 0)
        }
    
    def _apply_threshold_rule(self, value: float, thresholds: List[Dict[str, float]]) -> float:
        """Apply threshold-based translation"""
        for threshold in thresholds:
            if threshold['min'] <= value < threshold['max']:
                return threshold['output']
        return 0.0
    
    # ---------------------------------------------------------------- safe AST eval
    # eval() with a stripped __builtins__ is still escapable via dunder
    # access on literals (e.g. ().__class__.__bases__). We restrict the AST
    # to numeric literals, named variables, +-*/%**, unary neg, and a
    # whitelist of safe functions instead.

    _ALLOWED_BIN_OPS = {
        ast.Add: op.add, ast.Sub: op.sub,
        ast.Mult: op.mul, ast.Div: op.truediv, ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod, ast.Pow: op.pow,
    }
    _ALLOWED_UNARY_OPS = {ast.UAdd: op.pos, ast.USub: op.neg}
    _ALLOWED_FUNCS = {
        "min": min, "max": max, "round": round, "abs": abs,
        "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
    }

    def _safe_eval(self, expression: str, variables: Dict[str, float]) -> float:
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid formula syntax: {e}") from e

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.Constant):  # numbers only
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError(f"Disallowed constant: {node.value!r}")
            if isinstance(node, ast.Name):
                if node.id in variables:
                    return variables[node.id]
                raise ValueError(f"Unknown variable: {node.id}")
            if isinstance(node, ast.BinOp):
                opcls = type(node.op)
                if opcls not in self._ALLOWED_BIN_OPS:
                    raise ValueError(f"Disallowed operator: {opcls.__name__}")
                return self._ALLOWED_BIN_OPS[opcls](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp):
                opcls = type(node.op)
                if opcls not in self._ALLOWED_UNARY_OPS:
                    raise ValueError(f"Disallowed unary op: {opcls.__name__}")
                return self._ALLOWED_UNARY_OPS[opcls](_eval(node.operand))
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in self._ALLOWED_FUNCS:
                    raise ValueError("Only whitelisted functions are allowed")
                if node.keywords:
                    raise ValueError("Keyword arguments not allowed")
                args = [_eval(a) for a in node.args]
                return self._ALLOWED_FUNCS[node.func.id](*args)
            raise ValueError(f"Disallowed AST node: {type(node).__name__}")

        return float(_eval(tree))

    def _evaluate_formula(self, expression: str, national_value: float, sensitivity: Dict[str, float], company_factor: float) -> float:
        """Safely evaluate formula expression via restricted AST."""
        variables = {
            'national_value': float(national_value),
            'sensitivity': float(sensitivity['impact_multiplier']),
            'company_factor': float(company_factor),
        }
        try:
            result = self._safe_eval(expression, variables)
            return float(max(0, min(100, result)))
        except Exception as e:
            # Use logging instead of print so failures show up properly
            import logging
            logging.getLogger(__name__).warning(
                f"Formula evaluation error for {expression!r}: {e}"
            )
            return 0.0
