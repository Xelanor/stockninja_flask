from .auth import SignupApi, InitialLoginApi, PassLoginApi, GetUserNotifIdApi, GetUsersNotifIdsApi
from .portfolio import GetAllPortfoliosApi, GetPortfoliosApi, AddPortfolioItemApi, SetPortfolioBuyTarget, SetPortfolioSellTarget, PortfolioDeleteApi, GetSinglePortfolioApi
from .change import GetChangesApi, AddChangeItemApi
from .ticker import GetTickersApi, GetAllTickerDetailsApi, GetAllCurrencyDetailsApi, GetSingleTickerApi, GetSingleTickerDetailsApi, AddTickerItemApi, AddTickerScrapDataApi, TickerSearchApi
from .transaction import GetAllTransactionsApi, GetTransactionsApi, AddTransactionItemApi, DeleteTransactionItemApi, SetInformTransactionItemApi, SellTransactionItemApi, GetTracingTransactionsApi, SetCurrentPriceTransactionItemApi, SetTracedTransactionItemApi
from .notifications import GetNotificationsApi, AddNotificationItemApi, NotificationViewedApi, DeleteNotificationApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(InitialLoginApi, '/api/auth/login')
    api.add_resource(PassLoginApi, '/api/auth/login/<code>')
    api.add_resource(GetUserNotifIdApi, '/api/auth/user-notifid')
    api.add_resource(GetUsersNotifIdsApi, '/api/auth/notif-ids')

    api.add_resource(GetAllPortfoliosApi, '/api/portfolio/all')
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
    api.add_resource(GetAllCurrencyDetailsApi, '/api/ticker/currencies')
    api.add_resource(GetSingleTickerApi, '/api/ticker/single')
    api.add_resource(GetSingleTickerDetailsApi, '/api/ticker/single-details')
    api.add_resource(AddTickerItemApi, '/api/ticker/add')
    api.add_resource(AddTickerScrapDataApi, '/api/ticker/scrap')
    api.add_resource(TickerSearchApi, '/api/ticker/search')

    api.add_resource(GetAllTransactionsApi, '/api/transaction/all')
    api.add_resource(GetTransactionsApi, '/api/transaction')
    api.add_resource(AddTransactionItemApi, '/api/transaction/add')
    api.add_resource(DeleteTransactionItemApi, '/api/transaction/delete')
    api.add_resource(SetInformTransactionItemApi, '/api/transaction/inform')
    api.add_resource(SellTransactionItemApi, '/api/transaction/sell')
    api.add_resource(GetTracingTransactionsApi, '/api/transaction/tracing')
    api.add_resource(SetCurrentPriceTransactionItemApi,
                     '/api/transaction/set-current-price')
    api.add_resource(SetTracedTransactionItemApi,
                     '/api/transaction/set-traced')

    api.add_resource(GetNotificationsApi, '/api/notification')
    api.add_resource(AddNotificationItemApi, '/api/notification/add')
    api.add_resource(NotificationViewedApi, '/api/notification/viewed')
    api.add_resource(DeleteNotificationApi, '/api/notification/delete')
