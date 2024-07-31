MODEL_PRICING = {}

MODEL_PRICING["anthropic/claude-3-opus"] = {
    "input_price_per_token": 0.000015,  # $15 per million tokens
    "output_price_per_token": 0.000075,  # $75 per million tokens
    "image_price_per_thousand": 24,  # $24 per thousand images
}

MODEL_PRICING["anthropic/claude-3-sonnet"] = {
    "input_price_per_token": 0.000003,  # $3 per million tokens
    "output_price_per_token": 0.000015,  # $15 per million tokens
    "image_price_per_thousand": 4.8,  # $4.8 per thousand images
}

MODEL_PRICING["anthropic/claude-3.5-sonnet:beta"] = {
    "input_price_per_token": 0.000003,  # $3 per million tokens
    "output_price_per_token": 0.000015,  # $15 per million tokens
    "image_price_per_thousand": 4.8,  # $4.8 per thousand images
}

MODEL_PRICING["openai/gpt-4o-mini"] = {
    "input_price_per_token": 0.00000015,  # $0.15 per million tokens
    "output_price_per_token": 0.0000006,  # $0.6 per million tokens
    "image_price_per_thousand": 7.225,  # $7.225 per thousand images
}

MODEL_PRICING["anthropic/claude-3-haiku"] = {
    "input_price_per_token": 0.00000025,  # $0.25 per million tokens
    "output_price_per_token": 0.00000125,  # $1.25 per million tokens
    "image_price_per_thousand": 0.4,  # $0.4 per thousand images
}

MODEL_PRICING["meta-llama/llama-3-70b-instruct"] = {
    "input_price_per_token": 0.00000051,  # $0.51 per million tokens
    "output_price_per_token": 0.00000074,  # $0.74 per million tokens
    "image_price_per_thousand": 0,  # This model doesn't support image input
}

# ADD PRICING ABOVE THIS LINE, KEEP THIS LINE

def get_model_pricing(model: str):
    return MODEL_PRICING.get(model, {
        "input_price_per_token": 0,
        "output_price_per_token": 0,
        "image_price_per_thousand": 0,
    })
