import __init__
from models.database import engine
from models.model import Subscription, Payment
from sqlmodel import Session, select
from datetime import date, datetime

class SubscripitionService:
    def __init__(self,engine):
        self.engine = engine

    def create(self, subscription: Subscription):
        with Session(self.engine) as session:
            session.add(subscription)
            session.commit()
            return subscription
        
    def list_all(self):
        with Session(self.engine) as session:
            statement = select(Subscription)
            results = session.exec(statement).all()
        return results
    
    def _has_pay(self,results):
        for result in results:
            if result.date.month == date.today().month:
                return True
        return False

    def pay(self,subscription: Subscription):
        with Session(self.engine) as session:
            statement = select(Payment).join(Subscription).where(Subscription.empresa==subscription.empresa)
            results = session.exec(statement).all()
            print(results)
            if self._has_pay(results):
                question = input('Essa conta ja foi paga, deseja pagar novamento? Y ou N: ')
        
                if not question.upper() == 'Y':
                    return
            
            pay = Payment(subscription_id= subscription.id, date=date.today())
            session.add(pay)
            session.commit()

    def total_value(self):
       with Session(self.engine) as session:
            statement = select(Subscription)
            results = session.exec(statement).all()

       total = 0
       for result in results:
           total += result.valor
        
       return float(total)

    def delete(self,id):
        with Session(self.engine) as session:
            statement = select(Subscription).where(Subscription.id == id)
            result = session.exec(statement).one()
            session.delete(result)
            session.commit()
            
    def _get_last_12_months_native(self):
        today = datetime.now()
        year = today.year
        month = today.month
        last_12_months = []
        for _ in range(12):
            last_12_months.append((month,year))
            month -= 1
            if month == 0:
               month = 12
               year -= 1
        return last_12_months[::-1]

    def _get_values_for_months(self, last_12_month):
        with Session(self.engine) as session:
            statement = select(Payment)
            results = session.exec(statement).all()

            value_for_months = []
            for i in last_12_month:
                value = 0
                for result in results:
                    if result.date.month == i[0] and result.date.year == i[1]:
                        value += float(result.subscription.valor)
                value_for_months.append(value)
        return value_for_months

    def gen_chart(self):
        last_12_months = self._get_last_12_months_native()
        values_for_months = self._get_values_for_months(last_12_months)
        last_12_months2 = []
        for i in last_12_months:
            last_12_months2.append(i[0])
        print(last_12_months2)
        print(values_for_months)
        import matplotlib.pyplot as plt

        plt.plot(last_12_months2 , values_for_months)
        plt.show()

