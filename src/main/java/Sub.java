import org.zeromq.SocketType;
import org.zeromq.ZContext;
import org.zeromq.ZMQ;

import java.net.MalformedURLException;
import java.rmi.AlreadyBoundException;
import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.StringTokenizer;

import static java.lang.Integer.parseInt;

public class Sub implements SubRemoteInterface {
    private static Sub sub = null;
    private ZContext context = null;
    private ZMQ.Socket subscriberSocket = null;

    public Sub(String name) {
        try{
            SubRemoteInterface manager = (SubRemoteInterface) UnicastRemoteObject.exportObject(this,0);
            Registry rmiRegistry = LocateRegistry.getRegistry();
            rmiRegistry.rebind(name,manager);
            System.err.println("Sub ready");
        }
        catch(RemoteException e){
            e.printStackTrace();
        }

        context = new ZContext();
    }

    public static void main(String[] args) {
        sub = new Sub(args[0]);
    }

    @Override
    public int Get(String topicName) throws RemoteException {
        System.out.println("GET");
        return 0;
    }

    @Override
    public int Subscribe(String topic) throws RemoteException {
//        System.out.println("SUBS");
        //  Socket to talk to server
        this.subscriberSocket = context.createSocket(SocketType.SUB);
        subscriberSocket.connect(ProxyServer.XPUB_PORT);
        String filter = String.format("['%s'] ", topic);
        subscriberSocket.subscribe(filter.getBytes(ZMQ.CHARSET));
        System.out.println("Subscribed to topic: " + topic);
        return 0;
    }

    @Override
    public int Unsubscribe() throws RemoteException {
        System.out.println("UNSUB");
        return 0;
    }
}
