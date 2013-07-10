cymex: cymex.pyx
	cython cymex.pyx
	mkoctfile --mex cymex.c -I/usr/include/python2.7 -lpython2.7 -ldl

clean:
	rm -f *.o *~ *.mex *.h *.c *.pyc
