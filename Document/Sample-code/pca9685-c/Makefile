CC=gcc
CFLAG=-lbcm2835
INC=-I./include

pca9685tool: pca9685tool.c srcc
	$(CC) -c pca9685tool.c $(CFLAG) $(INC)
	$(CC) *.o -o p9 $(CFLAG)

srcc:
	cd ./src;make all
	cp ./src/*.o ./

clean:
	cd ./src;make clean
	rm *.o;rm p9
