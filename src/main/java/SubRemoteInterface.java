import java.rmi.Remote;
import java.rmi.RemoteException;

public interface SubRemoteInterface extends Remote {
    int Get(String topicName) throws RemoteException;

    int Subscribe(String topic) throws RemoteException;

    int Unsubscribe() throws RemoteException;
}