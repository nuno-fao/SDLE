package XPUB_XSUB;

import org.zeromq.SocketType;
import org.zeromq.ZContext;
import org.zeromq.ZMQ;
import org.zeromq.ZMQ.Poller;
import org.zeromq.ZMQ.Socket;

import java.util.Arrays;

/**
 * Simple request-reply broker
 *
 */
public class Proxy
{

    public static void main(String[] args)
    {
        //  Prepare our context and sockets
        try (ZContext context = new ZContext()) {
            Socket xsub = context.createSocket(SocketType.XSUB);
            Socket xpub = context.createSocket(SocketType.XPUB);
            xsub.bind("tcp://*:5559");
            xpub.bind("tcp://*:5560");

            System.out.println("launch and connect proxy.");

            //  Initialize poll set
            Poller items = context.createPoller(2);
            items.register(xsub, Poller.POLLIN);
            items.register(xpub, Poller.POLLIN);

            boolean more = false;
            byte[] message;

            //  Switch messages between sockets
            while (!Thread.currentThread().isInterrupted()) {
                //  poll and memorize multipart detection
                items.poll();

                if (items.pollin(0)) {
                    while (true) {
                        // receive message
                        message = xsub.recv(0);
                        System.out.println("Received xSub message: " + new String(message, ZMQ.CHARSET));
                        more = xsub.hasReceiveMore();

                        // Broker it
                        System.out.println(xpub.send(message, more ? ZMQ.SNDMORE : 0));
                        if (!more) {
                            break;
                        }
                    }
                }

                if (items.pollin(1)) {
                    while (true) {
                        // receive message
                        message = xpub.recv(0);
                        System.out.println("Received xPub message: " + new String(message, ZMQ.CHARSET));
                        more = xpub.hasReceiveMore();
                        // Broker it
                        System.out.println(xsub.send(message, more ? ZMQ.SNDMORE : 0));
                        if (!more) {
                            break;
                        }
                    }
                }
            }
        }
    }
}