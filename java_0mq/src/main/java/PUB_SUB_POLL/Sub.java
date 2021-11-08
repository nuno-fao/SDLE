package PUB_SUB_POLL;

import java.util.StringTokenizer;

import org.zeromq.SocketType;
import org.zeromq.ZMQ;
import org.zeromq.ZContext;

public class Sub {
    public static void main(String[] args)
    {
        try (ZContext context = new ZContext()) {
            //  Socket to talk to server
            System.out.println("Collecting updates from weather server");
            ZMQ.Socket subscriber1 = context.createSocket(SocketType.SUB);
            subscriber1.connect("tcp://localhost:5556");
            ZMQ.Socket subscriber2 = context.createSocket(SocketType.SUB);
            subscriber2.connect("tcp://localhost:5557");

            //  Subscribe to zipcode, default is NYC, 10001
            String filter = (args.length > 0) ? args[0] : "10001 ";
            subscriber1.subscribe(filter.getBytes(ZMQ.CHARSET));

            String filter2 = (args.length > 0) ? args[0] : "10001 ";
            subscriber2.subscribe(filter.getBytes(ZMQ.CHARSET));

            ZMQ.Poller poller = context.createPoller(2);
            poller.register(subscriber1, ZMQ.Poller.POLLIN);
            poller.register(subscriber2, ZMQ.Poller.POLLIN);


            while (!Thread.currentThread().isInterrupted()){
                //  Use trim to remove the tailing '0' character
                poller.poll();
                if (poller.pollin(0)){
                    String string = subscriber1.recvStr(0).trim();
                    System.out.println("Temperature from sub1: " + string);
                }
                if (poller.pollin(1)){
                    String string = subscriber2.recvStr(0).trim();
                    System.out.println("Temperature from sub2: " + string);
                }
            }
        }
    }
}
