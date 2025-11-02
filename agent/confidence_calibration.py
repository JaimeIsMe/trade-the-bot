# Add confidence calibration after _parse_llm_response
def _calibrate_confidence(self, decision, market_data):
    '''Calibrate confidence to correlate with trade quality'''
    llm_conf = decision.get('confidence', 50)
    tq = market_data.get('analysis', {}).get('trade_quality_score', 50)
    
    # Simple fix: confidence should closely follow trade quality
    # If LLM gave 45% but TQ is 75, boost it up
    # If LLM gave 45% but TQ is 35, reduce it down
    
    adjusted = tq + (llm_conf - 50) * 0.3  # 30% weight to LLM, 70% to TQ
    decision['confidence'] = max(0, min(100, adjusted))
    return decision
