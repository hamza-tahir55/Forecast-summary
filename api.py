from flask import Flask, request, jsonify
import os
from phi.agent import Agent
from phi.model.deepseek import DeepSeekChat

app = Flask(__name__)

# Set API keys
os.environ["DEEPSEEK_API_KEY"] = "sk-2e541143af014ebf8f70681786bf2ca2"
os.environ["OPENAI_API_KEY"] = "sk-2e541143af014ebf8f70681786bf2ca2"

@app.route("/forecast/summary", methods=["POST"])
def generate_summary():
    try:
        forecast_data = request.get_json()
        print("Raw request JSON:", forecast_data)


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

            {forecast_data}
            """],
            markdown=False,
            pip_install=False,
            structured_outputs=True,
        )

        result = summary_agent.run()
        return jsonify({"summary": result.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5002)
