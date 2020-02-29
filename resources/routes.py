from .auth import SignupApi, InitialLoginApi, PassLoginApi
from .portfolio import GetPortfoliosApi, AddPortfolioItemApi, SetPortfolioBuyTarget, SetPortfolioSellTarget, PortfolioDeleteApi, GetSinglePortfolioApi
from .change import GetChangesApi, AddChangeItemApi
from .ticker import GetTickersApi, GetAllTickerDetailsApi, GetSingleTickerApi, GetSingleTickerDetailsApi, AddTickerItemApi, AddTickerScrapDataApi, TickerSearchApi
from .transaction import GetTransactionsApi, AddTransactionItemApi, DeleteTransactionItemApi, SetInformTransactionItemApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(InitialLoginApi, '/api/auth/login')
    api.add_resource(PassLoginApi, '/api/auth/login/<code>')

    api.add_resource(GetPortfoliosApi, '/api/portfolio')
    api.add_resource(GetSinglePortfolioApi, '/api/portfolio/single')
    api.add_resource(AddPortfolioItemApi, '/api/portfolio/add')
    api.add_resource(SetPortfolioBuyTarget, '/api/portfolio/setbuytarget')
    api.add_resource(SetPortfolioSellTarget, '/api/portfolio/setselltarget')
    api.add_resource(PortfolioDeleteApi, '/api/portfolio/delete')

    api.add_resource(GetChangesApi, '/api/change')
    api.add_resource(AddChangeItemApi, '/api/change/add')

    api.add_resource(GetTickersApi, '/api/ticker')
    api.add_resource(GetAllTickerDetailsApi, '/api/ticker/all')
    api.add_resource(GetSingleTickerApi, '/api/ticker/single')
    api.add_resource(GetSingleTickerDetailsApi, '/api/ticker/single-details')
    api.add_resource(AddTickerItemApi, '/api/ticker/add')
    api.add_resource(AddTickerScrapDataApi, '/api/ticker/scrap')
    api.add_resource(TickerSearchApi, '/api/ticker/search')

    api.add_resource(GetTransactionsApi, '/api/transaction')
    api.add_resource(AddTransactionItemApi, '/api/transaction/add')
    api.add_resource(DeleteTransactionItemApi, '/api/transaction/delete')
    api.add_resource(SetInformTransactionItemApi, '/api/transaction/inform')
