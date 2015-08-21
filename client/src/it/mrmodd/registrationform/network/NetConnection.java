package it.mrmodd.registrationform.network;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;

import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import android.util.Base64;
import android.util.Log;

public class NetConnection {
	public static final String PARTICIPANTS_PATH = "participants/";
	public static final String ASSISTANCES_PATH = "assistances/";
	
	private HttpURLConnection connection;
	
	static {
		init_SSLSocket();
	}
	
	public NetConnection(String method, String url) throws IOException {
		URL urlObj = new URL(url);
		
		if (url.startsWith("https")) {
			connection = (HttpsURLConnection) urlObj.openConnection();
			Log.d("NetConnection", "Opening a secure connection");
		} else {
			connection = (HttpURLConnection) urlObj.openConnection();
			Log.d("NetConnection", "Opening an insecure connection");
		}
		
		connection.setRequestMethod(method);
		
		if (method.equalsIgnoreCase("POST") || method.equalsIgnoreCase("PUT")) {
			connection.setDoOutput(true);
			connection.setRequestProperty("Content-Type", "application/json");
		}
		connection.setDoInput(true);
		connection.setRequestProperty("Accept", "application/json");
	}
	
	public void setCredential(String user, String password) {
		String credentials = user + ":" + password;
		connection.setRequestProperty("Authorization", "Basic " + Base64.encodeToString(credentials.getBytes(), Base64.DEFAULT));
	}
	
	public String readString() throws IOException {
		InputStream content = connection.getInputStream();
		BufferedReader in = new BufferedReader (new InputStreamReader(content));
		String line;
		String string = "";
		while ((line = in.readLine()) != null) {
			string += line+"\n";
		}
		content.close();
		in.close();
		
		Log.d("NetConnection", "readString(): server body response: " + string);
		
		return string;
	}
	
	public void writeString(String message) throws IOException {
		Log.d("NetConnection", "writeString(): client body request: " + message);
		
		OutputStream os = connection.getOutputStream();
		DataOutputStream dos = new DataOutputStream(os);
		dos.write(message.getBytes("UTF-8"));
		dos.write('\n');
		dos.flush();
		dos.close();
		os.close();
	}
	
	public int getResponseCode() throws IOException {
		return connection.getResponseCode();
	}
	
	public String getResponseMessage() throws IOException {
		return connection.getResponseMessage();
	}
	
	public void disconnect() {
		Log.d("NetConnection", "Disconnecting from the server");
		connection.disconnect();
	}
	
	private static void init_SSLSocket() {
		Log.d("NetConnection", "Setting up SSL socket options");
		
		// Disable hostname checking for server url into the SSL certificate
		HttpsURLConnection.setDefaultHostnameVerifier(new javax.net.ssl.HostnameVerifier(){

			@Override
			public boolean verify(String arg0, SSLSession arg1) {
				Log.d("NetConnection", "Hostname from SSL cert: " + arg0);
				return true;
			}
			
		});
		
		// Create a trust manager that does not validate certificate chains
		TrustManager[] trustAllCerts = new TrustManager[] { 
		    new X509TrustManager() {

				@Override
				public void checkClientTrusted(
						java.security.cert.X509Certificate[] chain,
						String authType) {
				}

				@Override
				public void checkServerTrusted(
						java.security.cert.X509Certificate[] chain,
						String authType) {
				}

				@Override
				public java.security.cert.X509Certificate[] getAcceptedIssuers() {
					return null;
				}
		    } 
		};
		
		try {
			
			SSLContext sc = SSLContext.getInstance("SSL");
		    sc.init(null, trustAllCerts, new SecureRandom()); 
		    HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
		    
		} catch (NoSuchAlgorithmException | KeyManagementException e) {
			Log.e("NetConnection", "Error setting up SSL connectiton.");
		}
	}
}
