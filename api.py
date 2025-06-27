from flask import Flask, request, jsonify
import os
from phi.agent import Agent
from phi.model.deepseek import DeepSeekChat
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  

# Set API keys
os.environ["DEEPSEEK_API_KEY"] = "sk-2e541143af014ebf8f70681786bf2ca2"
os.environ["OPENAI_API_KEY"] = "sk-2e541143af014ebf8f70681786bf2ca2"


@app.route("/ping")
def ping():
    return "pong"

@app.route("/", methods=["GET"])
def health_check():
    return "API is alive", 200


@app.route("/forecast/summary", methods=["POST"])
def generate_summary():
    try:
        data = request.get_json()
        forecast_data = data.get("data", {})
        currency = data.get("currency")

        
        def filter_forecast_data(data_list):
            def parse_date(date_str):
                for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except Exception:
                        continue
                return None

            def filter_entries(entries, category_name=None):
                actual_dates = [
                    parse_date(e.get("date"))
                    for e in entries
                    if e.get("is_actual") is True and parse_date(e.get("date")) is not None
                ]
                if not actual_dates:
                    if category_name:
                        print(f"[{category_name}] No actual entries found.")
                    return entries

                latest_actual = max(actual_dates)
                cutoff = latest_actual - relativedelta(months=18)

                if category_name:
                    print(f"[{category_name}] Latest actual: {latest_actual.strftime('%d-%m-%Y')}, "
                        f"Cutoff: {cutoff.strftime('%d-%m-%Y')}")

                return [
                    e for e in entries
                    if (e.get("is_actual") is True and parse_date(e.get("date")) >= cutoff)
                    or (e.get("is_actual") is False)
                ]

            if not isinstance(data_list, list):
                raise ValueError("Expected a list of categories.")

            filtered_data = []
            for item in data_list:
                if "sum_values" in item and isinstance(item["sum_values"], list):
                    item_copy = dict(item)
                    item_copy["sum_values"] = filter_entries(item["sum_values"], item.get("category", ""))
                    filtered_data.append(item_copy)
                else:
                    filtered_data.append(item)

            return filtered_data

        new_forecast_data = filter_forecast_data(forecast_data)


        # Define agent
        summary_agent = Agent(
            name="Summary Agent",
            role="Generates business forecast summary",
            model=DeepSeekChat(),
            instructions=[f"""
            Generate a concise, easy-to-understand summary of the user's forecast. The forecast is based on historical actuals and uses a data-driven, time-sensitive modelling technique that captures trends and seasonality.

            Summarise the forecasted values for:
            - Income
            - Cost of Sales
            - Gross Margin (%)
            - Expenses
            - EBITDA
            - Total Assets & Liabilities
            - Net Cash In/Out

            Provide a professional ~150-200 word summary highlighting key trends, stability, or volatility. Reference reliability from historical performance in a financial advisor tone. Use data from the provided forecast below:

            {new_forecast_data}

            Return the summary in clean, readable Markdown using headings (###), bold text, bullet points, and clear line breaks.

            You must use following currency symbol {currency}.

            """],
            markdown=True,
            pip_install=False,
            structured_outputs=True,
        )

        result = summary_agent.run("How much data of actuals in months you have for each KPI)
        return jsonify({"summary": result.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


