## 7/14/18
## Amy Olex and Luke Maffey
## run.sh provides a one command option to running Chrono without having to remember the long command or data locations
## 
## Edit the script to add in additional options as needed.
## I have one option for my laptop using the training data, and two options for willow, one with training and the other with test.
## I have not added in any evaluation options yet.

USER=$1  ##Options: amy, luke
LOC=$2  ##Options: willow, laptop
DATASET=$3  ##Options: test, train
ML=$4		##Chrono options
ML_DATA=$5 	##Options: news5, news3, clin5, clin3, newsclin5, newsclin3


## Example Usage:  ./run.sh amy laptop train NB news5

## Below are the variables to change for each user if the data locations change
if [ $USER = "amy" ]
then
	if [ $LOC = "laptop" ]
	then
		ANAFORA_DIR="/Users/alolex/Desktop/VCU_PhD_Work/Chrono/anaforatools"

		if [ $DATASET = "test" ]
		then
			DATA_DIR="/Users/alolex/Desktop/VCU_PhD_Work/Chrono/data/THYME"
			OUT_DIR="/Users/alolex/Desktop/VCU_PhD_Work/Chrono/results/Colon_dev"
			ML_DATA_DIR="/Users/alolex/Desktop/VCU_PhD_Work/Chrono/sample_files"
		fi
		if [ $DATASET = "train" ]
		then
			DATA_DIR="/Users/alolex/Desktop/VCU_PhD_Work/Chrono/data/THYME"
			OUT_DIR="/Users/alolex/Desktop/VCU_PhD_Work/Chrono/results/Colon_dev"
			ML_DATA_DIR="/Users/alolex/Desktop/VCU_PhD_Work/Chrono/sample_files"
		fi
		if [ $ML_DATA = "news5" ]
		then
			ML_DATA_FILE="official_train_MLmatrix_Win5_012618_data.csv"
			ML_CLASS_FILE="official_train_MLmatrix_Win5_012618_class.csv"
		fi
		if [ $ML_DATA = "newsclin5" ]
		then
			ML_DATA_FILE="Newswire-THYMEColon_train_Win5_data.csv"
			ML_CLASS_FILE="Newswire-THYMEColon_train_Win5_class.csv"
		
		fi
		if [ $ML_DATA = "clin5" ]
		then
			ML_DATA_FILE="THYMEColon_train_Win5_data.csv"
                        ML_CLASS_FILE="THYMEColon_train_Win5_class.csv"
		fi
		if [ $ML_DATA = "newsclin3" ]
                then
                        ML_DATA_FILE="Newswire-THYMEColon_train_Win3_data.csv"
                        ML_CLASS_FILE="Newswire-THYMEColon_train_Win3_class.csv"

                fi
		if [ $ML_DATA = "news3" ]
                then
                        ML_DATA_FILE="official_train_MLmatrix_Win3_data.csv"
                        ML_CLASS_FILE="official_train_MLmatrix_Win3_class.csv"
                fi


	fi
	
	if [ $LOC = "willow" ]
	then
		ANAFORA_DIR="/home/alolex/ChronoAnalysis_031918/anaforatools"

		if [ $DATASET = "test" ]
		then
			DATA_DIR="/home/share/data/THYME/ColonTrainData/input"
			OUT_DIR="/home/alolex/ChronoAnalysis_031918/ChronoResults/colonTrain_baselineTest"
			ML_DATA_DIR="/home/alolex/ChronoAnalysis_031918/Chrono/sample_files"
		fi
		if [ $DATASET = "train" ]
		then
			DATA_DIR="/home/alolex/THYME_Data/THYMEColonFinal_Train/input"
			OUT_DIR="/home/alolex/ChronoAnalysis_031918/ChronoResults/colonTrain_dev2"
			ML_DATA_DIR="/home/alolex/ChronoAnalysis_031918/Chrono/sample_files"
		fi
		if [ $ML_DATA = "news5" ]
		then
			ML_DATA_FILE="official_train_MLmatrix_Win5_012618_data.csv"
			ML_CLASS_FILE="official_train_MLmatrix_Win5_012618_class.csv"
		fi
		if [ $ML_DATA = "newsclin5" ]
		then
			ML_DATA_FILE="Newswire-THYMEColon_train_Win5_data.csv"
			ML_CLASS_FILE="Newswire-THYMEColon_train_Win5_class.csv"
		
		fi
		if [ $ML_DATA = "clin5" ]
		then
			ML_DATA_FILE="THYMEColon_train_Win5_data.csv"
                        ML_CLASS_FILE="THYMEColon_train_Win5_class.csv"
		fi
		if [ $ML_DATA = "newsclin3" ]
                then
                        ML_DATA_FILE="Newswire-THYMEColon_train_Win3_data.csv"
                        ML_CLASS_FILE="Newswire-THYMEColon_train_Win3_class.csv"

                fi
		if [ $ML_DATA = "news3" ]
                then
                        ML_DATA_FILE="official_train_MLmatrix_Win3_data.csv"
                        ML_CLASS_FILE="official_train_MLmatrix_Win3_class.csv"
                fi


	fi
	
	
	
	
	
	python Chrono.py -i $DATA_DIR -o $OUT_DIR -m $ML -d $ML_DATA_DIR/$ML_DATA_FILE -c $ML_DATA_DIR/$ML_CLASS_FILE

	cd $ANAFORA_DIR
	
	python -m anafora.evaluate -r $DATA_DIR -p $OUT_DIR --exclude Event

fi

