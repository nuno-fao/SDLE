import org.zeromq.SocketType;
import org.zeromq.ZContext;
import org.zeromq.ZMQ;

public class ProxyServer {
    public static String XSUB_PORT = "tcp://*:5559";
    public static String XPUB_PORT = "tcp://*:5560";


    public static void main(String[] args)
    {
        //  Prepare our context and sockets
        try (ZContext context = new ZContext()) {
            ZMQ.Socket xsub = context.createSocket(SocketType.XSUB);
            ZMQ.Socket xpub = context.createSocket(SocketType.XPUB);
            xsub.bind("tcp://*:5559");
            xpub.bind("tcp://*:5560");

            System.out.println("launch and connect proxy.");

            //  Initialize poll set
            ZMQ.Poller items = context.createPoller(2);
            items.register(xsub, ZMQ.Poller.POLLIN);
            items.register(xpub, ZMQ.Poller.POLLIN);

            ZMQ.proxy(xsub, xpub, null);
        }
    }
}
