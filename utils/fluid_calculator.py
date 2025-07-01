class FluidCalculator:
    """Pediatric fluid calculation using various methods"""
    
    @staticmethod
    def maintenance_holliday_segar(weight_kg: float) -> dict:
        """
        Holliday-Segar method for maintenance fluid calculation
        - First 10 kg: 100 mL/kg/day
        - Next 10 kg: 50 mL/kg/day  
        - Each kg above 20 kg: 20 mL/kg/day
        """
        if weight_kg <= 0:
            return {"error": "Weight must be positive"}
        
        if weight_kg <= 10:
            ml_per_day = weight_kg * 100
        elif weight_kg <= 20:
            ml_per_day = (10 * 100) + ((weight_kg - 10) * 50)
        else:
            ml_per_day = (10 * 100) + (10 * 50) + ((weight_kg - 20) * 20)
        
        ml_per_hour = ml_per_day / 24
        
        return {
            "method": "Maintenance (Holliday-Segar)",
            "ml_per_day": round(ml_per_day, 1),
            "ml_per_hour": round(ml_per_hour, 1),
            "details": f"Calculated for {weight_kg} kg patient"
        }
    
    @staticmethod
    def resuscitation_fluid(weight_kg: float) -> dict:
        """
        Resuscitation fluid calculation
        Standard: 20 mL/kg bolus
        """
        if weight_kg <= 0:
            return {"error": "Weight must be positive"}
        
        bolus_ml = weight_kg * 20
        
        return {
            "method": "Resuscitation",
            "bolus_ml": round(bolus_ml, 1),
            "details": f"20 mL/kg bolus for {weight_kg} kg patient",
            "administration": "Give as rapid IV bolus, may repeat if needed"
        }
    
    @staticmethod
    def deficit_calculation(weight_kg: float, dehydration_percent: float) -> dict:
        """
        Deficit calculation based on dehydration percentage
        Deficit = Weight (kg) × Dehydration (%) × 10
        """
        if weight_kg <= 0:
            return {"error": "Weight must be positive"}
        
        if dehydration_percent < 0 or dehydration_percent > 20:
            return {"error": "Dehydration percentage should be between 0-20%"}
        
        deficit_ml = weight_kg * dehydration_percent * 10
        
        # Calculate replacement over 24 hours
        ml_per_hour_replacement = deficit_ml / 24
        
        # Add maintenance fluid
        maintenance = FluidCalculator.maintenance_holliday_segar(weight_kg)
        total_ml_per_hour = ml_per_hour_replacement + maintenance["ml_per_hour"]
        total_ml_per_day = deficit_ml + maintenance["ml_per_day"]
        
        return {
            "method": f"Deficit Replacement ({dehydration_percent}% dehydration)",
            "deficit_ml": round(deficit_ml, 1),
            "ml_per_hour_replacement": round(ml_per_hour_replacement, 1),
            "maintenance_ml_per_hour": round(maintenance["ml_per_hour"], 1),
            "total_ml_per_hour": round(total_ml_per_hour, 1),
            "total_ml_per_day": round(total_ml_per_day, 1),
            "details": f"Replace deficit over 24 hours + maintenance for {weight_kg} kg patient"
        }
    
    @staticmethod
    def dehydration_assessment(weight_kg: float, age_years: float, scenario: str) -> dict:
        """
        Calculate fluids based on different dehydration scenarios
        """
        if scenario == "Mild Dehydration (5%)":
            return FluidCalculator.deficit_calculation(weight_kg, 5)
        elif scenario == "Moderate Dehydration (10%)":
            return FluidCalculator.deficit_calculation(weight_kg, 10)
        elif scenario == "Severe Dehydration (15%)":
            return FluidCalculator.deficit_calculation(weight_kg, 15)
        else:
            return {"error": "Unknown dehydration scenario"}
    
    @staticmethod
    def calculate_all_scenarios(weight_kg: float, age_years: float) -> dict:
        """Calculate all fluid scenarios for comparison"""
        results = {}
        
        # Maintenance
        results["maintenance"] = FluidCalculator.maintenance_holliday_segar(weight_kg)
        
        # Resuscitation
        results["resuscitation"] = FluidCalculator.resuscitation_fluid(weight_kg)
        
        # Different dehydration levels
        results["mild_dehydration"] = FluidCalculator.deficit_calculation(weight_kg, 5)
        results["moderate_dehydration"] = FluidCalculator.deficit_calculation(weight_kg, 10)
        results["severe_dehydration"] = FluidCalculator.deficit_calculation(weight_kg, 15)
        
        return results
