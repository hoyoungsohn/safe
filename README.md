# SAFE (Suicidal Attempts Finding Engine)
## 소개
<b>SAFE는 SNS 상의 자살/자해 사진 및 동영상을 인공지능으로 판별하여 관련기관에 리포팅합니다.</b>

구체적으로는, 인스타그램에 올라온 자살, 자해 관련 자료를 검색하여, 대표 사진을 인공지능(딥러닝) 이미지 분류기(Turi Create)로 자해 사진/동영상인지 판별 후, 자해 영상일 경우 관련기관(중앙자살예방센터)에 리포팅 합니다.
```
*Overall Process:
  인스타그램 크롤링 → 자살/자해 관련 글의 대표 사진 확보
  → 인공지능 신경망으로 자해 영상 판별 → 자해 영상 포함 글만 리스팅 → 리포팅(중앙자살예방센터)
```
## 자해 영상 학습 자료
인스타그램에서 '#자해' 해시태그로 검색하여 모은 이미지(320x320, jpg) 8,367장을 자해(3,150장)와 자해인지 불확실(5,217장)한 것 2가지로 직접 분류하여 학습자료를 구축하였습니다. 자해 영상인지 분류하는 기준은, (1)신체 부위가 사진에 나와있는지, (2)최근에 발생한 상처인지로 하였습니다.

[Turi Create](https://github.com/apple/turicreate)의 Image Classifier 기능을 사용하여, 신경망 Resnet을 사용해 학습시켰습니다. 전체 데이터셋을 무작위로 나누어 80%를 트레이닝셋으로 사용하였고, 20%를 테스트셋으로 사용하여 성능을 검증하였습니다(90% 이상 정확도).

자료의 제약으로 대부분 팔에 상처를 입고 피를 흘리고 있는 영상을 학습하게 되었습니다. 일단 확실한 것 위주로 동작할 수 있도록, 직접적으로 신체 부위가 나와있지 않고 피만 나와있거나 한 영상은 일단 불확실한 것으로 분류하였습니다. 추후 데이터셋을 업데이트하여 좀더 분류를 세분화/고도화 할 필요가 있습니다.

## 프로그램 실행환경
기본적으로 Windows 10에서 개발하였으나, Image Classification을 위해 사용한 [Turi Create](https://github.com/apple/turicreate)이 Native Windows는 지원하지 않아, WSL(Windows Subsystem for Linux)의 <b>ubuntu 18.04</b>에서 동작을 확인하였습니다.

* Firefox를 사용하는 Web crawler를 포함하고 있어, Linux에 Firefox와 geckodriver를 설치하셔야 합니다.
  * Firefox
  ```shell
  sudo apt-get install firefox
  ```
  * geckodriver
  - https://github.com/mozilla/geckodriver/releases
  - 압축을 풀어서 나오는 geckodriver 실행파일을 ```/usr/bin/```, ```~/anaconda3/``` 등 PATH 추가된 곳에 넣기

* Anaconda3 5.2.0 사용하여 가상환경 내에서 실행하였습니다.
  - 혹시 설치가 필요한 경우 다음 글을 참조하세요: https://www.digitalocean.com/community/tutorials/how-to-install-anaconda-on-ubuntu-18-04-quickstart

## Requirement
[Turi Create](https://github.com/apple/turicreate)이 권장하는 대로 가상환경 내에 설치하였습니다. Anaconda의 가상환경을 사용하였습니다.
```conda create --name turi python=3.6.6 anaconda```로 가상환경(이름: turi, 다른 것으로도 가능)을 생성하고, ```source activate turi```로 가상환경으로 들어갔습니다. *(2018.10.2. 현재, Python 3.7이 막 출시되었으나 이 코드를 작성하면서는 Turi Create이 Python 3.7 버전에서 잘 동작하는지 검증하지 못했고, Turi Create 중에서도 확인 중이라고 하여, Python 3.6.6 버전을 이용하였습니다)* <br>
이 안에서 아래 명령어를 입력하시면, 필요한 패키지(oauthlib, turicreate, selenium, msgpack, mime, openpyxl)를 설치하게 됩니다.
```shell
pip install -r requirements.txt
```
* turicreate
  * Apple에서 만든 Machine Learning 모델을 만들어주는 툴입니다.
  * 혹시 설치가 잘 안 되면, linux의 경우 의존성으로 인해 [관련 설명](https://github.com/apple/turicreate/blob/master/LINUX_INSTALL.md) 참조해서 설치가 필요합니다.
  ```shell
  sudo apt update
  sudo apt-get install -y libblas3 liblapack3 libstdc++6 python-setuptools)
  ```
  * oauthlib이 필요하여 함께 설치됩니다.
* selenium
  * 웹크롤링 위해 필요한 패키지입니다.
  * msgpack이 필요하여 함께 설치됩니다.
* mime
  * 이메일 전송 시 필요합니다.
* openpyxl
  * 엑셀파일을 다루기 위해서 필요합니다.

## Further Works
### 영상분류
자살시도 방법에 다양한 형태가 있으므로 데이터셋을 업데이트하여 현재 자해/불확실(2분류)로 되어 있는 것을 좀더 세분화/고도화 할 필요가 있습니다. 데이터셋은 직접 만들었지만, 이미지의 저작권은 원저작자(업로더)에게 있으므로 데이터셋을 공개적으로 배포하는 것은 어려울 것 같습니다. 필요하신 경우 따로 연락주시면 논의하도록 하겠습니다.

### 자연어처리
현재 중앙자살예방센터 기준으로, 자살 관련 게시물을 평가하는 데 있어서 글 내용에서 (1)분류, (2)자살위험도, (3)주 호소문제를 파악하게 되어있습니다. 해당 게시물에서 상기 3가지를 찾아내는 문제는 현재 코드로는 구현하지 못했습니다.<br>
*(현재 코드는 실제 자해를 실행한 이미지를 포함한 게시물을 찾아내므로, 상기 문제를 매우 제한적으로만 해결할 수 있습니다: (1)분류: 자살실행 사진/동영상, (2)자살위험도: 자살방법, 사진 또는 동영상 포함 여부, (3)주 호소문제: 미상)*

* 분류 (택1)
  * 동반자살모집
  * 구체적자살방법 제공
  * *자살실행 사진/동영상 (현재 코드로는 이 분류만 확인 가능)*
  * 독극물판매
  * 기타 생명경시정보
* 자살위험도 (유/무, 항목별 중복 가능)
  * 동반자살모집 / 연락처 / 자살계획 / 자살방법 / 시행예고 / 시도경험 / 자살유가족 / 우울증 / 사진 / 동영상
* 주 호소문제 (유/무, 항목별 중복 불가)
  * 가정문제 / 경제생활 / 남녀문제 / 사별 / 육체적질병 / 정신적질병 / 직장 업무 / 학대, 폭력 / 기타문제 / 미상
