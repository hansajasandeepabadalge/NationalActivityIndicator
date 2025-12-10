from typing import Dict, Any, List

def get_indicator_value(code: str, national_indicators: Dict[str, Any]) -> float:
    """Helper to get national indicator value"""
    indicators = national_indicators.get('indicators', [])
    for ind in indicators:
        if ind['indicator_code'] == code:
            return ind.get('current_value', 0.0)
    return 0.0

def calculate_transportation_availability(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
    """
    How easily can people/goods move?
    """
    road_status = get_indicator_value('ENV_ROAD_STATUS', national_indicators)
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    weather = get_indicator_value('ENV_WEATHER_SEV', national_indicators)
    unrest = get_indicator_value('POL_UNREST_01', national_indicators)
    
    base_score = 100.0
    
    if road_status < 70:
        base_score -= (70 - road_status) * 0.5
    
    if fuel_avail < 50:
        base_score -= (50 - fuel_avail) * 0.8
    
    if weather > 60:
        base_score -= (weather - 60) * 0.6
    
    if unrest > 70:
        base_score -= (unrest - 70) * 1.0
    
    return max(0.0, min(100.0, base_score))

def calculate_workforce_availability(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
    """
    Can employees reach workplace and perform their duties?
    """
    transport_avail = calculate_transportation_availability(national_indicators, company_profile)
    health_alerts = get_indicator_value('SOCIAL_HEALTH_ALERTS', national_indicators)
    strike_activity = get_indicator_value('POL_STRIKE_ACTIVITY', national_indicators)
    safety = get_indicator_value('SOCIAL_SAFETY_PERCEPTION', national_indicators)
    
    base_score = 100.0
    
    transport_impact = (100 - transport_avail) * 0.4
    base_score -= transport_impact
    
    if health_alerts > 50:
        health_impact = (health_alerts - 50) * 0.3
        base_score -= health_impact
    
    if strike_activity > 60:
        strike_impact = (strike_activity - 60) * 0.4
        base_score -= strike_impact
    
    if safety < 50:
        safety_impact = (50 - safety) * 0.3
        base_score -= safety_impact
    
    return max(0.0, min(100.0, base_score))

def calculate_supply_chain_integrity(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
    """
    Can supplies reach the business?
    """
    port_ops = get_indicator_value('ECON_PORT_OPS', national_indicators)
    road_status = get_indicator_value('ENV_ROAD_STATUS', national_indicators)
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    import_policy = get_indicator_value('LEGAL_IMPORT_POLICY', national_indicators)
    currency = get_indicator_value('ECON_CURRENCY_STAB', national_indicators)
    
    import_dep = company_profile.get('supply_chain', {}).get('import_dependency', 0.5)
    
    supply_chain_score = (
        port_ops * 0.30 * import_dep +
        road_status * 0.25 +
        fuel_avail * 0.25 +
        import_policy * 0.10 * import_dep +
        currency * 0.10 * import_dep
    )
    
    local_sourcing = 1 - import_dep
    resilience_bonus = local_sourcing * 10
    
    final_score = supply_chain_score + resilience_bonus
    
    return max(0.0, min(100.0, final_score))

def calculate_operational_cost_pressure(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
    """
    Are operating costs increasing?
    """
    fuel_prices = get_indicator_value('ECON_FUEL_PRICES', national_indicators)
    inflation = get_indicator_value('ECON_INFLATION_PRESSURE', national_indicators)
    currency = get_indicator_value('ECON_CURRENCY_STAB', national_indicators)
    wage_pressure = get_indicator_value('SOCIAL_WAGE_PRESSURE', national_indicators)
    
    cost_pressure = 0.0
    
    fuel_dependency = company_profile.get('critical_dependencies', {}).get('fuel', 'medium')
    fuel_weight = {'critical': 0.40, 'high': 0.30, 'medium': 0.20, 'low': 0.10}
    
    if fuel_prices > 50:
        cost_pressure += (fuel_prices - 50) * fuel_weight.get(fuel_dependency, 0.20)
    
    if inflation > 50:
        cost_pressure += (inflation - 50) * 0.30
    
    import_dep = company_profile.get('supply_chain', {}).get('import_dependency', 0.5)
    if currency < 50:
        cost_pressure += (50 - currency) * 0.20 * import_dep
    
    if wage_pressure > 50:
        cost_pressure += (wage_pressure - 50) * 0.15
    
    return max(0.0, min(100.0, cost_pressure))

def calculate_regulatory_compliance_status(national_indicators: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
    """
    Are there new compliance requirements or changes?
    """
    legal_changes = get_indicator_value('LEGAL_REGULATORY_CHANGES', national_indicators)
    tax_changes = get_indicator_value('LEGAL_TAX_POLICY', national_indicators)
    
    compliance_burden = (
        legal_changes * 0.60 +
        tax_changes * 0.40
    )
    
    return max(0.0, min(100.0, compliance_burden))
