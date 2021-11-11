val inputPath = "hdfs://server-1:9000/user/vagrant/alice.txt"
val outputPath = "spark-alice-wordcount-output"

val textFile = sc.textFile(inputPath)
val counts = textFile.flatMap(line => line.split(" "))                        .filter(line => line.matches("[A-Za-z]+")))
                     .map(word => (word, 1))
                     .reduceByKey(_ + _)
                     .map(p => (p._2,  p._1))
                     .sortByKey(false, 1)
                     .map(p => s"${p._1}\t${p._2}")
counts.saveAsTextFile(outputPath)