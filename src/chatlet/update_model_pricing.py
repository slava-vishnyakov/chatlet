import re

import requests

def main():
    url = "https://openrouter.ai/api/v1/models"

    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()


        with open("model_pricing.py", "w") as file:
            file.write("MODEL_PRICING = {}\n\n")


            for model in sorted(data["data"], key=lambda x: x["id"]):
                model_id = model["id"]
                pricing = model["pricing"]

                const_name = f"MODEL_{re.sub(r'[^a-zA-Z0-9_]', '_', model_id.upper())}"

                file.write(f'{const_name} = "{model_id}"\n')
                file.write(f'MODEL_PRICING[{const_name}] = {{\n')
                file.write(f'    "input_price_per_token": {pricing["prompt"]},\n')
                file.write(f'    "output_price_per_token": {pricing["completion"]},\n')
                file.write(f'    "image_price_per_thousand": {pricing["image"]},\n')
                file.write('}\n\n')

            file.write("# ADD PRICING ABOVE THIS LINE, KEEP THIS LINE\n\n")
            file.write("")
            file.write("def get_model_pricing(model: str):\n")
            file.write("    return MODEL_PRICING.get(model, {\n")
            file.write("        \"input_price_per_token\": 0,\n")
            file.write("        \"output_price_per_token\": 0,\n")
            file.write("        \"image_price_per_thousand\": 0,\n")
            file.write("    })\n")

        print("Model pricing information has been written to model_pricing.py")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

if __name__ == '__main__':
    main()