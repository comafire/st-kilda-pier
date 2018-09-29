# St. Kilda Pier

St. Kilda Pier(SKP)는 Big Data 를 이용하여 Data Science 를 하기 위한 Docker 기반 중소형 클러스터를 쉽게 구축 할 수 있도록 지원하는 플랫폼입니다.

Amazon, Azure 등 Cloud 벤더들의 서비스를 이용하면 비슷한 서비스를 더 간편히 이용할 수 있지만, 데이터 보안, 운영비용등 여러 이유로 클라우드를 사용할 수 없는 오픈소스 중심의 중소형 Big Data Cluster가 필요한 분들을 위하여 개발되고 있습니다.

SKP는 Docker 기반으로 Cloud 벤더들의 Virtual Machine상에서도 설치 가능합니다.

SKP는 Python Invoke, SSH Remote Command, Docker-Machine 를 이용해 Docker를 이용한 Big Data Cluster 구축 시 필요한 컨테이너 이미지 및 명령어 셋을 지원합니다.

Architecture

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-001.png"></img>

Support Docker Container
* Jupyter
  * Jupyter Kernel: Python2/3, Scala, R, Julia, Go
  * Jupyter Kernel Gateway
  * Data Science Library
    * Python2/3: tensorflow CPU/GPU, pytorch CPU/GPU, keras, pandas, scikit-learn, .. etc
* Spark
* Airflow
* Portainer
* Kafka
* Zookeeper
* Nginx
* Flask

클러스터 설치에 대한 자세한 사항은 doc 디렉토리 안에 Markdown 파일을 참조하세요.

Document
* [01-cluster.md](https://github.com/comafire/st-kilda-pier/blob/master/doc/01-cluster.md)
* [02-docker.md](https://github.com/comafire/st-kilda-pier/blob/master/doc/02-docker.md)

SKP 를 이용하여 Data Science Project 를 진행하는 예제는 아래 공유 Repository 를 참조하세요.

* notebooks-skp: https://github.com/comafire/notebooks-skp

Single Node 용 Docker Jupyter CPU/GPU Image 는 아래 Repository를 이용하세요.

* docker-jupyter: https://github.com/comafire/docker-jupyter


_**St. Kilda Pier는 호주 멜버른에 위치한 리틀 펭귄이 서식하는 작고 아름다운 부두입니다.**_
