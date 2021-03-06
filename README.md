# JurisBERT - Brazilian Legal Text Dataset
Brazilian Legal Text Dataset for trainning transformer based models.

## Requeriments
Before run, you have to install in your path a Firefox WebDriver for Selenium.
Download last release at <https://github.com/mozilla/geckodriver/releases>
Put executable file in PATH.

## Get Started
Run command below to install all required dependencies.

```shell
pip install -r requirements.txt
```

## Generate MLM Dataset
To generate a dataset for MLM pre-trainning.
Run the command below to execute all pipeline that will generate 2 files in `output/mlm/`.

```shell
python mlm.py all
```

To run individual tasks, you can pass a task as parameter:

```shell
python mlm.py scrap
python run.py parse
python run.py export
```

## Generate STS Dataset
To generate a dataset for STS fine-tunning.
Run the command below to execute all pipeline that will generate files in `output/sts/{sts_type}/`.

```shell
python sts.py all --sts_type "binary | scale | triplet | benchmark"
```

## Generated Datasets
If you are interested in downloading only the pre-generated datasets, just use the links below:

[MLM datasets](./resources/mlm)

[STS for train datasets](./resources/sts/scale)

[STS for benchmark datasets](./resources/sts/benchmark)

[Raw datasets](./resources/raw)
