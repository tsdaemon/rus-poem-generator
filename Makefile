export DATASETS_PATH:=$(HOME)/.classic-ai-local-data
export PYTHONPATH:=$(PWD)

download:
	rm -rf ./data
	mkdir data
	wget https://github.com/sberbank-ai/classic-ai/raw/master/examples/phonetic-baseline/data/words_accent.json.bz2 -P ./data
	wget http://rusvectores.org/static/models/web_upos_cbow_300_20_2017.bin.gz -P ./data
	gzip -d web_upos_cbow_300_20_2017.bin.gz
	wget https://github.com/buriy/russian-nlp-datasets/releases/download/r1/stress.tar.gz -P ./data
	tar -C ./data -xzf ./data/stress.tar.gz
	rm ./data/stress.tar.gz
	mv ./data/stress/stress.txt ./data/stress.txt
	rm -rf ./data/stress/

	rm -rf ~/.classic-ai-local-data
	mkdir ~/.classic-ai-local-data
	wget https://raw.githubusercontent.com/sberbank-ai/classic-ai/master/data/classic_poems.json -P $(DATASETS_PATH)
	wget https://bucketeer-db1966c9-c9f8-427d-ae61-659a91a9fca7.s3.amazonaws.com/public/sdsj2017_sberquad.csv -P $(DATASETS_PATH)

preprocess:
	python ./scripts/serialize_word_forms.py

server:
	python server.py

testspeed:
	py.test tests/test_speed.py -v -s

testworks:
	py.test tests/test_it_works.py -v

make test:
	make testworks
	make testspeed

