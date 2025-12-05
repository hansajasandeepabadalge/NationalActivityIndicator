from typing import Dict, Any
from .universal_indicators import get_indicator_value, calculate_transportation_availability, calculate_workforce_availability, calculate_supply_chain_integrity

def calculate_retail_footfall_impact(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    For retail businesses: How will store foot traffic be affected?
    """
    base_footfall = 1000  # Default if not in profile
    # In a real scenario, we'd sum up footfall from all locations
    
    adjustment = 1.0
    
    weather = get_indicator_value('ENV_WEATHER_SEV', national_indicators)
    if weather > 60:
        weather_factor = 1 - ((weather - 60) / 40 * 0.30)
        adjustment *= weather_factor
    
    transport_avail = calculate_transportation_availability(national_indicators, company_profile)
    transport_factor = transport_avail / 100
    adjustment *= (0.7 + transport_factor * 0.3)
    
    consumer_conf = get_indicator_value('ECON_CONSUMER_CONF', national_indicators)
    confidence_factor = consumer_conf / 100
    adjustment *= (0.8 + confidence_factor * 0.2)
    
    safety = get_indicator_value('SOCIAL_SAFETY_PERCEPTION', national_indicators)
    safety_factor = safety / 100
    adjustment *= (0.75 + safety_factor * 0.25)
    
    unrest = get_indicator_value('POL_UNREST_01', national_indicators)
    if unrest > 70:
        unrest_factor = 1 - ((unrest - 70) / 30 * 0.40)
        adjustment *= unrest_factor
    
    adjusted_footfall = base_footfall * adjustment
    impact_percentage = ((adjusted_footfall - base_footfall) / base_footfall) * 100
    
    return {
        'value': impact_percentage,  # This is the indicator value (negative means drop)
        'base_footfall': base_footfall,
        'expected_footfall': adjusted_footfall,
        'impact_percentage': impact_percentage
    }

def calculate_manufacturing_capacity(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
    """
    For manufacturers: What % of production capacity can be utilized?
    """
    capacity = 100.0
    
    power_reliability = get_indicator_value('ENV_POWER_RELIABILITY', national_indicators)
    if power_reliability < 100:
        capacity *= (power_reliability / 100)
    
    supply_chain = calculate_supply_chain_integrity(national_indicators, company_profile)
    if supply_chain < 80:
        material_factor = supply_chain / 100
        capacity *= (0.5 + material_factor * 0.5)
    
    workforce_avail = calculate_workforce_availability(national_indicators, company_profile)
    workforce_factor = workforce_avail / 100
    capacity *= workforce_factor
    
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    if fuel_avail < 50:
        fuel_factor = 0.7 + (fuel_avail / 100 * 0.3)
        capacity *= fuel_factor
    
    return max(0.0, min(100.0, capacity))

def calculate_logistics_fleet_availability(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    For logistics companies: What % of fleet can operate?
    """
    total_fleet = company_profile.get('business_scale', {}).get('fleet_size', 50)
    available_fleet = float(total_fleet)
    
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    fuel_factor = fuel_avail / 100
    available_fleet *= fuel_factor
    
    road_status = get_indicator_value('ENV_ROAD_STATUS', national_indicators)
    unrest = get_indicator_value('POL_UNREST_01', national_indicators)
    
    if road_status < 70 or unrest > 70:
        route_factor = min(road_status, 100 - unrest) / 100
        available_fleet *= (0.6 + route_factor * 0.4)
    
    workforce_avail = calculate_workforce_availability(national_indicators, company_profile)
    driver_factor = workforce_avail / 100
    available_fleet *= driver_factor
    
    fleet_availability_pct = (available_fleet / total_fleet) * 100 if total_fleet > 0 else 0
    
    return {
        'value': fleet_availability_pct,
        'total_fleet': total_fleet,
        'available_vehicles': int(available_fleet),
        'availability_percentage': fleet_availability_pct
    }
