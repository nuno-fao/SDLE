import java.net.MalformedURLException;
import java.rmi.AlreadyBoundException;
import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

import static java.lang.Integer.parseInt;

public class Sub implements SubRemoteInterface {
    private static Sub sub = null;

    public Sub(String name, int port) {
        try{
            SubRemoteInterface manager = (SubRemoteInterface) UnicastRemoteObject.exportObject(this,0);
            Registry rmiRegistry = LocateRegistry.createRegistry(port);
            rmiRegistry.bind(name,manager);
            System.err.println("Sub ready");
        }
        catch(RemoteException | AlreadyBoundException e){
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        sub = new Sub(args[0],parseInt(args[1]));
    }

    @Override
    public int Get() throws RemoteException {
        System.out.println("GET");
        return 0;
    }

    @Override
    public int Subscribe() throws RemoteException {
        System.out.println("SUBS");
        return 0;
    }

    @Override
    public int Unsubscribe() throws RemoteException {
        System.out.println("UNSUB");
        return 0;
    }
}
