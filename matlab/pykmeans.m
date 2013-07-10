function labels = pykmeans(X, k)

cymex('w', 'X', X)
cymex('x', sprintf('X = X.reshape(%d, %d)', size(X, 1), size(X, 2)))
cymex('x', 'from sklearn.cluster import KMeans');
cymex('x', sprintf('km = KMeans(k=%d)', k));
cymex('x', 'km.fit(X)')
labels = cymex('r', 'km.labels_')

