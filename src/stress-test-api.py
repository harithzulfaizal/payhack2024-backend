from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Numeric, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON

# Database connection parameters
conn_params = "postgresql://neondb_owner:CG4zi5OygUKb@ep-flat-band-a1icda59.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(conn_params)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# SQLAlchemy model for the 'stress_test_results' table
class StressTestResults(Base):
    __tablename__ = 'stress_test_results'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    stress_test_id = Column(Integer, nullable=False)
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)

# SQLAlchemy model for the 'stress_test_parameters' table
class StressTestParameters(Base):
    __tablename__ = 'stress_test_parameters'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, nullable=False)
    scenario = Column(String, nullable=False)
    income_salary = Column(Numeric)
    fixed_expenses_housing = Column(Numeric)
    fixed_expenses_utilities = Column(Numeric)
    fixed_expenses_insurance = Column(Numeric)
    variable_expenses_groceries = Column(Numeric)
    variable_expenses_transport = Column(Numeric)
    variable_expenses_lifestyle = Column(Numeric)
    variable_expenses_healthcare = Column(Numeric)
    loans_mortgage = Column(Numeric)
    loans_car_loan = Column(Numeric)
    loans_personal_loan = Column(Numeric)
    loans_credit_card_debt = Column(Numeric)
    investments_stock_market = Column(Numeric)
    investments_retirement_funds = Column(Numeric)
    investments_mutual_funds = Column(Numeric)
    savings_emergency_fund = Column(Numeric)
    savings_vacation_fund = Column(Numeric)
    savings_general_savings = Column(Numeric)
    savings_other_savings = Column(Numeric)

# Pydantic models for request validation
class Income(BaseModel):
    Salary: float

class FixedExpenses(BaseModel):
    Housing: float
    Utilities: float
    Insurance: float

class VariableExpenses(BaseModel):
    Groceries: float
    Transport: float
    Lifestyle: float
    Healthcare: float

class Expenses(BaseModel):
    FixedExpenses: FixedExpenses
    VariableExpenses: VariableExpenses

class Loans(BaseModel):
    Mortgage: float
    CarLoan: float
    PersonalLoan: float
    CreditCardDebt: float

class Investments(BaseModel):
    StockMarket: float
    RetirementFunds: float
    MutualFunds: float

class Savings(BaseModel):
    EmergencyFund: float
    VacationFund: float
    GeneralSavings: float
    OtherSavings: float

class StressTestParametersInput(BaseModel):
    user_id: int
    scenario: str
    Income: Income
    Expenses: Expenses
    Loans: Loans
    Investments: Investments
    Savings: Savings

# Initialize FastAPI app
app = FastAPI()

# Endpoint to create stress test parameters
@app.post("/stress-test-parameters")
def create_stress_test_parameters(params: StressTestParametersInput):
    session = SessionLocal()
    try:
        stress_test_param = StressTestParameters(
            user_id=params.user_id,
            scenario=params.scenario,
            income_salary=params.Income.Salary,
            fixed_expenses_housing=params.Expenses.FixedExpenses.Housing,
            fixed_expenses_utilities=params.Expenses.FixedExpenses.Utilities,
            fixed_expenses_insurance=params.Expenses.FixedExpenses.Insurance,
            variable_expenses_groceries=params.Expenses.VariableExpenses.Groceries,
            variable_expenses_transport=params.Expenses.VariableExpenses.Transport,
            variable_expenses_lifestyle=params.Expenses.VariableExpenses.Lifestyle,
            variable_expenses_healthcare=params.Expenses.VariableExpenses.Healthcare,
            loans_mortgage=params.Loans.Mortgage,
            loans_car_loan=params.Loans.CarLoan,
            loans_personal_loan=params.Loans.PersonalLoan,
            loans_credit_card_debt=params.Loans.CreditCardDebt,
            investments_stock_market=params.Investments.StockMarket,
            investments_retirement_funds=params.Investments.RetirementFunds,
            investments_mutual_funds=params.Investments.MutualFunds,
            savings_emergency_fund=params.Savings.EmergencyFund,
            savings_vacation_fund=params.Savings.VacationFund,
            savings_general_savings=params.Savings.GeneralSavings,
            savings_other_savings=params.Savings.OtherSavings
        )
        session.add(stress_test_param)
        session.commit()
        session.refresh(stress_test_param)
        return {"message": "Stress test parameters created", "id": stress_test_param.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

# Endpoint to retrieve stress test parameters by user_id
@app.get("/stress-test-parameters/{user_id}")
def get_stress_test_parameters(user_id: int):
    session = SessionLocal()
    try:
        parameters = session.query(StressTestParameters).filter(StressTestParameters.user_id == user_id).all()
        if not parameters:
            raise HTTPException(status_code=404, detail="Stress test parameters not found")
        result = []
        for param in parameters:
            param_data = {
                "id": param.id,
                "created_at": param.created_at,
                "user_id": param.user_id,
                "scenario": param.scenario,
                "Income": {
                    "Salary": float(param.income_salary) if param.income_salary is not None else None
                },
                "Expenses": {
                    "FixedExpenses": {
                        "Housing": float(param.fixed_expenses_housing) if param.fixed_expenses_housing is not None else None,
                        "Utilities": float(param.fixed_expenses_utilities) if param.fixed_expenses_utilities is not None else None,
                        "Insurance": float(param.fixed_expenses_insurance) if param.fixed_expenses_insurance is not None else None
                    },
                    "VariableExpenses": {
                        "Groceries": float(param.variable_expenses_groceries) if param.variable_expenses_groceries is not None else None,
                        "Transport": float(param.variable_expenses_transport) if param.variable_expenses_transport is not None else None,
                        "Lifestyle": float(param.variable_expenses_lifestyle) if param.variable_expenses_lifestyle is not None else None,
                        "Healthcare": float(param.variable_expenses_healthcare) if param.variable_expenses_healthcare is not None else None
                    }
                },
                "Loans": {
                    "Mortgage": float(param.loans_mortgage) if param.loans_mortgage is not None else None,
                    "CarLoan": float(param.loans_car_loan) if param.loans_car_loan is not None else None,
                    "PersonalLoan": float(param.loans_personal_loan) if param.loans_personal_loan is not None else None,
                    "CreditCardDebt": float(param.loans_credit_card_debt) if param.loans_credit_card_debt is not None else None
                },
                "Investments": {
                    "StockMarket": float(param.investments_stock_market) if param.investments_stock_market is not None else None,
                    "RetirementFunds": float(param.investments_retirement_funds) if param.investments_retirement_funds is not None else None,
                    "MutualFunds": float(param.investments_mutual_funds) if param.investments_mutual_funds is not None else None
                },
                "Savings": {
                    "EmergencyFund": float(param.savings_emergency_fund) if param.savings_emergency_fund is not None else None,
                    "VacationFund": float(param.savings_vacation_fund) if param.savings_vacation_fund is not None else None,
                    "GeneralSavings": float(param.savings_general_savings) if param.savings_general_savings is not None else None,
                    "OtherSavings": float(param.savings_other_savings) if param.savings_other_savings is not None else None
                }
            }
            result.append(param_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

# Endpoint to retrieve stress test results by user_id
@app.get("/stress-test-results/{user_id}")
def get_stress_test_result(user_id: int):
    session = SessionLocal()
    try:
        # Query the database for stress test results by user_id
        results = session.query(StressTestResults).filter(StressTestResults.user_id == user_id).all()
        if not results:
            raise HTTPException(status_code=404, detail="Stress test results not found")
        
        # Serialize results into JSON-friendly format
        result_data = []
        for result in results:
            result_data.append({
                "id": result.id,
                "user_id": result.user_id,
                "stress_test_id": result.stress_test_id,
                "result": result.result,  # This is already JSON
                "created_at": result.created_at,
            })
        
        return {"stress_test_results": result_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

# Run the app
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("stress-test-api:app", host="127.0.0.1", port=8000, reload=True)