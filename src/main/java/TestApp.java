import java.net.MalformedURLException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;

public class TestApp {

    public static void main(String[] args) throws MalformedURLException, NotBoundException, RemoteException {

        if (args.length < 2)
            throw new IllegalArgumentException("Not enough arguments");


        String accessPoint = args[0];

        switch (args[1]) {
            case "Get" -> {
                SubRemoteInterface server;
                server = (SubRemoteInterface) Naming.lookup("//" + accessPoint);
                System.out.println(server.Get(args[2]));
            }
            case "Put" -> {
                PubRemoteInterface server;
                server = (PubRemoteInterface) Naming.lookup("//" +accessPoint);
                System.out.println(server.Put());
            }
            case "Subscribe" -> {
                SubRemoteInterface server;
                server = (SubRemoteInterface) Naming.lookup(accessPoint);
                System.out.println(server.Subscribe(args[2]));
            }
            case "Unsubscribe" -> {
                SubRemoteInterface server;
                server = (SubRemoteInterface) Naming.lookup("//" +accessPoint);
                System.out.println(server.Unsubscribe());
            }
            default -> {
                throw new IllegalArgumentException("Illegal argument" + args[1]);
            }
        }
    }
}
