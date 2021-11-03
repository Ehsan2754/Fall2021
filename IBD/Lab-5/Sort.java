import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import java.util.stream.Collectors;
import java.util.StringTokenizer;
public class Sort {

  public static class SortMapper
       extends Mapper<Object, Text, IntWritable, Text>{


    public void map(Object key, Text value, Context context
                    ) throws IOException, InterruptedException {
        StringTokenizer tok = new StringTokenizer(value.toString());
        Text text = new Text(tok.nextToken());
        Integer frequency = Integer.parseInt(tok.nextToken());

        context.write(new IntWritable(frequency), text);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "word count");
    job.setJarByClass(Sort.class);
    job.setMapperClass(SortMapper.class);
    job.setOutputKeyClass(IntWritable.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}