import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold,cross_val_score,GridSearchCV
import numpy as np
import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

def gradient_boosting():
    # загружаем датасет
    features = pd.read_csv('features.csv', index_col='match_id')

    # получаем кол-во записей в датасете
    rows_num = features.shape[0]

    # заполняем пустоты в признаках
    for f, n in features.count().items():
        if n != rows_num:
            features[f].fillna(99999, inplace=True)
            #выводим признаки с пропусками
            print(features[f])

    # формируем матрицы
    X = features.loc[:, 'lobby_type':'dire_first_ward_time']
    y = features['radiant_win']

    # инициализируем массив с кол-вом деревьев
    n_trees = [30]
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    start_time = datetime.datetime.now()
    for n in n_trees:
        clf = GradientBoostingClassifier(n_estimators=n, random_state=241, verbose=True)
        clf.fit(X, y)
        scores.append(cross_val_score(clf, X, y, cv=kf, scoring='roc_auc').mean())

    time_ = datetime.datetime.now() - start_time

    # выводим итоговые значения оценок
    print(scores)
    # выводим затраченное время
    print(time_)


#процедура подбора параметра С для логистической регрессии
def l2_regression_first_test():
    #загружаем датасет
    features = pd.read_csv('features.csv',index_col='match_id')

    #получаем кол-во записей в датасете
    rows_num = features.shape[0]

    #заполняем пустоты в признаках
    for f,n in features.count().items():
        if n != rows_num:
            features[f].fillna(features[f].mean(),inplace=True)

    #формируем матрицы
    X = features.loc[:,'lobby_type':'dire_first_ward_time']
    y = features['radiant_win']

    #масштабируем признаки
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    #инициализируем кросс-валидатор
    kf = KFold(n_splits=5,shuffle=True,random_state=42)

    #инициализируем грид с параметром
    grid = {'C': np.power(10.0, np.arange(-5, 5))}

    #инициализируем логистическую регрессию
    clf=LogisticRegression(random_state=241)

    #инициализируем поисковик параметра
    gs = GridSearchCV(clf,grid,scoring='roc_auc',cv=kf)

    #ставим отметку времени начала обучения
    start_time = datetime.datetime.now()
    gs.fit(X,y)

    #вычисляем потраченное время
    time_ = datetime.datetime.now() - start_time
    print(time_)

    #выводим полученные значения по точности и соответствующее значение параметра
    for a in gs.grid_scores_:
        print(a.mean_validation_score,'__',a.parameters)

#процедура подбора параметра С для логистической регрессии без категориальных признаков в датасете
def l2_regression_no_categorical_features_test():
    # загружаем датасет
    features = pd.read_csv('features.csv', index_col='match_id')

    # получаем кол-во записей в датасете
    rows_num = features.shape[0]

    # заполняем пустоты в признаках
    for f, n in features.count().items():
        if n != rows_num:
            features[f].fillna(features[f].mean(), inplace=True)

    features_list = []
    #заполняем массив наименований признаков
    for f in list(features.columns):
        if not any(f==i for i in ['start_time','lobby_type','radiant_win','duration']) \
                and 'hero' not in f and 'status' not in f:
            features_list.append(f)
            print(f)

    #формируем матрицы
    X = features.loc[:,features_list]
    y = features['radiant_win']

    # инициализируем кросс-валидатор
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    # инициализируем грид с параметром
    grid = {'C': np.power(10.0, np.arange(-5, 5))}

    # инициализируем логистическую регрессию
    clf = LogisticRegression(random_state=241)

    # инициализируем поисковик параметра
    gs = GridSearchCV(clf, grid, scoring='roc_auc', cv=kf)

    # ставим отметку времени начала обучения
    start_time = datetime.datetime.now()
    gs.fit(X, y)

    # вычисляем потраченное время
    time_ = datetime.datetime.now() - start_time
    print(time_)

    #выводим полученные значения качества и соответствующие параметры
    for a in gs.grid_scores_:
        print(a.mean_validation_score, '__', a.parameters)

#процедура вычисления уникального количества героев в датасете
def count_unique_heros():
    # загружаем датасет
    features = pd.read_csv('features.csv', index_col='match_id')

    # получаем кол-во записей в датасете
    rows_num = features.shape[0]

    # заполняем пустоты в признаках
    for f, n in features.count().items():
        if n != rows_num:
            features[f].fillna(features[f].mean(), inplace=True)

    values = []
    #заполняем массив наименований признаков
    for f in list(features.columns):
        if 'hero' in f:
            values.append(f)

    #решейпим матрицу в вектор
    df1 = pd.lreshape(features,{'hero':values})

    #выводим кол-во уникальных значений (героев)
    print(df1['hero'].value_counts().shape[0])

#процедура тестирования логистической регрессии на "мешке слов№
def bag_of_words_test():
    #искусственно увеличим размер массива (т.к. в датасете имеются пропуски)
    N = 112

    #считываем данные
    features = pd.read_csv('features.csv', index_col='match_id')

    #инициализируем нулевую матрицу заданного размера (мешок слов)
    X_pick = np.zeros((features.shape[0],N))

    #заполняем мешок слов
    for i,match_id in enumerate(features.index):
        for p in range(5):
            X_pick[i, features.ix[match_id, 'r%d_hero' % (p + 1)] - 1] = 1
            X_pick[i, features.ix[match_id, 'd%d_hero' % (p + 1)] - 1] = -1

    values = []
    #заполняем массив наименований признаков
    for f in list(features.columns):
        if not any(f==i for i in ['start_time','match_id','radiant_win','duration']) \
                and 'hero' not in f and 'status' not in f:
            values.append(f)

    #инициализируем матрицу с "нужными" признаками
    X_ = features.loc[:, values]

    #соединяем 2 датафрейма
    X = pd.DataFrame(np.hstack((X_.values,X_pick)))

    #инициализируем целевой вектор
    y = features['radiant_win']

    #получаем кол-во записей в датасете
    rows_num = features.shape[0]

    # заполняем пустоты в признаках
    for f, n in X.count().items():
        if n != rows_num:
            X[f].fillna(X[f].mean(), inplace=True)

    # инициализируем кросс-валидатор
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    # инициализируем грид с параметром
    grid = {'C': np.power(10.0, np.arange(-5, 5))}

    # инициализируем логистическую регрессию
    clf = LogisticRegression(random_state=241)

    # инициализируем поисковик параметра
    gs = GridSearchCV(clf, grid, scoring='roc_auc', cv=kf)

    # ставим отметку времени начала обучения
    start_time = datetime.datetime.now()
    gs.fit(X, y)

    # вычисляем потраченное время
    time_ = datetime.datetime.now() - start_time
    print(time_)

    # выводим полученные значения качества и соответствующие параметры
    for a in gs.grid_scores_:
        print(a.mean_validation_score, '__', a.parameters)

def min_max_value():

    N = 112

    # загружаем датасет
    features = pd.read_csv('features.csv', index_col='match_id')
    features_test = pd.read_csv('features_test.csv', index_col='match_id')

    X_bow_train = np.zeros((features.shape[0],N))
    X_bow_test = np.zeros((features_test.shape[0], N))

    # заполняем мешок слов
    for i, match_id in enumerate(features.index):
        for p in range(5):
            X_bow_train[i, features.ix[match_id, 'r%d_hero' % (p + 1)] - 1] = 1
            X_bow_train[i, features.ix[match_id, 'd%d_hero' % (p + 1)] - 1] = -1

    # заполняем мешок слов
    for i, match_id in enumerate(features_test.index):
        for p in range(5):
            X_bow_test[i, features_test.ix[match_id, 'r%d_hero' % (p + 1)] - 1] = 1
            X_bow_test[i, features_test.ix[match_id, 'd%d_hero' % (p + 1)] - 1] = -1

    values = []
    # заполняем массив наименований признаков
    for f in list(features.columns):
        if not any(f == i for i in ['start_time', 'match_id', 'radiant_win', 'duration']) \
                and 'hero' not in f and 'status' not in f:
            values.append(f)

    # получаем кол-во записей в датасете
    rows_num = features.shape[0]

    # заполняем пустоты в признаках
    for f, n in features.count().items():
        if n != rows_num:
            features[f].fillna(99999, inplace=True)

    # заполняем пустоты в признаках
    for f, n in features_test.count().items():
        if n != rows_num:
            features_test[f].fillna(99999, inplace=True)

    # формируем матрицы
    X_train = features.loc[:, 'lobby_type':'dire_first_ward_time']
    X_test = features_test.loc[:, 'lobby_type':'dire_first_ward_time']
    y_train = features['radiant_win']

    # инициализируем матрицу с "нужными" признаками
    X_train_ = features.loc[:, values]
    # соединяем 2 датафрейма
    X_train = pd.DataFrame(np.hstack((X_train_.values, X_bow_train)))

    # инициализируем матрицу с "нужными" признаками
    X_test_ = features_test.loc[:, values]
    # соединяем 2 датафрейма
    X_test = pd.DataFrame(np.hstack((X_test_.values, X_bow_test)))

    # инициализируем целевой вектор
    y_train = features['radiant_win']

    # инициализируем логистическую регрессию
    clf = LogisticRegression(random_state=241)
    clf.fit(X_train,y_train)

    predictions = clf.predict_proba(X_test)

    print(max(predictions[:,1]),"____",min(predictions[:,1]))

min_max_value()



