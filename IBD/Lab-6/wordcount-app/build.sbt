name := "spark-wordcount"

version := "1.0"

scalaVersion := "2.12.15"
val sparkVersion = "3.2.0"


libraryDependencies += "org.apache.spark" %% "spark-core" % sparkVersion
// https://mvnrepository.com/artifact/org.apache.spark/spark-core
//libraryDependencies += "org.apache.spark" %% "spark-core" % "3.2.0"

