DATASETS_PATH:=$(HOME)/.classic-ai-local-data

download:
	rm -rf ./data
	mkdir data
	wget https://github.com/sberbank-ai/classic-ai/raw/master/examples/phonetic-baseline/data/words_accent.json.bz2 -P ./data

	rm -rf ~/.classic-ai-local-data
	mkdir ~/.classic-ai-local-data
	wget https://raw.githubusercontent.com/sberbank-ai/classic-ai/master/data/classic_poems.json -P $(DATASETS_PATH)
	wget https://bucketeer-db1966c9-c9f8-427d-ae61-659a91a9fca7.s3.amazonaws.com/public/sdsj2017_sberquad.csv -P $(DATASETS_PATH)
	wget http://rusvectores.org/static/models/web_upos_cbow_300_20_2017.bin.gz -P $(DATASETS_PATH)
server:
	python server.py