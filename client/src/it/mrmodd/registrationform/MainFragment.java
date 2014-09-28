package it.mrmodd.registrationform;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Date;

import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.app.Fragment;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Base64;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

public class MainFragment extends Fragment {
	private Button buttonQR;
	private Button buttonID;
	private Button buttonAccept;
	private Button buttonRemove;
	private Button buttonCancel;
	
	private TextView textViewCurrentID;
	
	private EditText editTextID;
	
	private Integer currentID = 0;
	private JSONObject currentJSON = null;
	
	
	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		
		View v = inflater.inflate(R.layout.fragment_main, container, false);
		
		buttonQR = (Button) v.findViewById(R.id.button_qr);
		buttonID = (Button) v.findViewById(R.id.button_id);
		buttonAccept = (Button) v.findViewById(R.id.button_accept);
		buttonRemove = (Button) v.findViewById(R.id.button_remove);
		buttonCancel = (Button) v.findViewById(R.id.button_cancel);
		
		textViewCurrentID = (TextView) v.findViewById(R.id.text_currentID);
		
		editTextID = (EditText) v.findViewById(R.id.editText_id);
		
		buttonQR.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				try {

				    Intent intent = new Intent("com.google.zxing.client.android.SCAN");
				    intent.putExtra("SCAN_MODE", "QR_CODE_MODE"); // "PRODUCT_MODE for bar codes

				    startActivityForResult(intent, 0);

				} catch (Exception e) {

				    Uri marketUri = Uri.parse("market://details?id=com.google.zxing.client.android");
				    Intent marketIntent = new Intent(Intent.ACTION_VIEW,marketUri);
				    
				    cleanScreen();
				    
				    startActivity(marketIntent);

				}
			}
			
		});
		
		buttonID.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				String id = editTextID.getText().toString();
				
				if (id.length() == 0) {
					Toast.makeText(getActivity(), R.string.error_empty_field, Toast.LENGTH_SHORT).show();
					return;
				}
				if (!id.matches("[0-9]+")) {
					Toast.makeText(getActivity(), R.string.error_invalid_field, Toast.LENGTH_SHORT).show();
					return;
				}
				
				editTextID.setText("");
				
				cleanScreen();
				
				currentID = Integer.parseInt(id);
        		new RetrieveDetails().execute();
				
			}
			
		});
		
		buttonAccept.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				
				if (currentID == 0) {
					Toast.makeText(getActivity(), R.string.error_no_id_selected, Toast.LENGTH_SHORT).show();
					return;
				}
				
				new CheckInID().execute();
			}
			
		});
		
		buttonRemove.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				
				if (currentID == 0) {
					Toast.makeText(getActivity(), R.string.error_no_id_selected, Toast.LENGTH_SHORT).show();
					return;
				}
				
				new CheckOutID().execute();
			}
			
		});
		
		buttonCancel.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				
				cleanScreen();
				
			}
			
		});
		
		return v;
	}
	
	@Override
	public void onActivityResult(int requestCode, int resultCode, Intent data) {           
	    super.onActivityResult(requestCode, resultCode, data);
	    if (requestCode == 0) {

	        if (resultCode == Activity.RESULT_OK) {
	        	String qr = data.getStringExtra("SCAN_RESULT");
	        	if (qr.matches("[0-9]+")) {
	        		
	        		currentID = Integer.parseInt(qr);
	        		new RetrieveDetails().execute();
	        		
	        	}
	        	else
	        		Toast.makeText(getActivity(), R.string.error_qr_content, Toast.LENGTH_SHORT).show();
	        }
	        if(resultCode == Activity.RESULT_CANCELED){
	            //handle cancel
	        }
	    }
	}
	
	private void cleanScreen() {
		currentID = 0;
		currentJSON = null;
		textViewCurrentID.setText(R.string.text_empty);
		editTextID.setText("");
	}
	
	private HttpURLConnection enstablishConnection(String method, String file) throws IOException {
		SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(getActivity());
		
		String url_pref = pref.getString(getActivity().getString(R.string.pref_key_server_url), "");
		String credentials = pref.getString(getActivity().getString(R.string.pref_key_username), "")
								+ ":"
								+ pref.getString(getActivity().getString(R.string.pref_key_password), "");
		URL url;
		HttpURLConnection connection;
		
		url = new URL(url_pref + file);
		
		connection = (HttpURLConnection) url.openConnection();
		connection.setRequestMethod(method);
		
		if (method.equalsIgnoreCase("POST") || method.equalsIgnoreCase("PUT"))
			connection.setDoOutput(true);
		connection.setDoInput(true);
		
		connection.setRequestProperty("Authorization", "Basic " + Base64.encodeToString(credentials.getBytes(), Base64.DEFAULT));
		
		return connection;
	}
	
	private String fetchJSON(HttpURLConnection conn) throws IOException {
		InputStream content = conn.getInputStream();
		BufferedReader in = new BufferedReader (new InputStreamReader(content));
		String line;
		String json = "";
		while ((line = in.readLine()) != null) {
			json += line;
		}
		content.close();
		in.close();
		
		return json;
	}
	
	private void writeJSON(HttpURLConnection conn, String json) throws IOException {
		
		conn.setRequestProperty("Content-Type", "application/json");
		conn.setRequestProperty("Content-Length", "" + json.getBytes("UTF-8").length);
		
		OutputStream os = conn.getOutputStream();
		DataOutputStream dos = new DataOutputStream(os);
		dos.write(json.getBytes("UTF-8"));
		dos.flush();
		dos.close();
		os.close();
		
	}
	
	class RetrieveDetails extends AsyncTask<Void, String, String> {

		@Override
		protected String doInBackground(Void... params) {
			String newtext = null;
			
			HttpURLConnection conn = null;
			try {
				conn = enstablishConnection("GET", currentID.toString() + "/");
				
				if (conn.getResponseCode() == 200) {
					
					String json = fetchJSON(conn);

					//Parse JSON
					currentJSON = new JSONObject(json);
					
					String first_name = currentJSON.getString("first_name");
					String last_name = currentJSON.getString("last_name");
					String email = currentJSON.getString("email");
					Boolean morning = currentJSON.getBoolean("participate_morning");
					Boolean afternoon = currentJSON.getBoolean("participate_afternoon");
					String checkin = (!currentJSON.getString("check_in").matches("null")) ? currentJSON.getString("check_in") : "--";
					String comments = currentJSON.getString("comments");

					newtext = getActivity().getString(R.string.text_currentID) + " " + currentID.toString() + "\n";
					newtext += getActivity().getString(R.string.text_name) + " " + first_name + "\n";
					newtext += getActivity().getString(R.string.text_lastname) + " " + last_name + "\n";
					newtext += getActivity().getString(R.string.text_email) + " " + email + "\n";
					newtext += getActivity().getString(R.string.text_morning) + " " + morning + "\n";
					newtext += getActivity().getString(R.string.text_afternoon) + " " + afternoon + "\n";
					newtext += getActivity().getString(R.string.text_check_in) + " " + checkin + "\n\n";
					newtext += getActivity().getString(R.string.text_comments) + "\n" + comments;
		            
				}
				else {
					publishProgress(getActivity().getString(R.string.error_server_code) + "\n" + conn.getResponseCode() + ": " + conn.getResponseMessage());
				}
				
			} catch (IOException | IllegalArgumentException e) {
				publishProgress(getActivity().getString(R.string.error_connection));
				e.printStackTrace();
			} catch (JSONException e) {
				publishProgress(getActivity().getString(R.string.error_invalid_response));
				e.printStackTrace();
			} finally {
				if (conn != null)
					conn.disconnect();
			}
			
			return newtext;
		}
		
		@Override
		protected void onProgressUpdate(String... values) {
			Toast.makeText(getActivity(), values[0], Toast.LENGTH_SHORT).show();
		}
		
		@Override
		protected void onPostExecute(String result) {
			if (result != null)
				textViewCurrentID.setText(result);
		}
	}
	
	class CheckInID extends AsyncTask<Void, String, Void> {

		@Override
		protected Void doInBackground(Void... params) {
			
			HttpURLConnection conn = null;
			try {
				conn = enstablishConnection("PUT", currentID.toString() + "/");
				
				if (currentJSON != null) {
					if (!currentJSON.getString("check_in").matches("null"))
						publishProgress(getActivity().getString(R.string.error_already_checked_in));
					else {
						String date = new java.sql.Timestamp(new Date().getTime()).toString();
						currentJSON.put("check_in", date);
						
						writeJSON(conn, currentJSON.toString());
						
						if (conn.getResponseCode() == 200) {
							publishProgress(conn.getResponseMessage());
							fetchJSON(conn);
						}
						else
							publishProgress(getActivity().getString(R.string.error_server_code) + "\n" + conn.getResponseCode() + ": " + conn.getResponseMessage());
					}
				}
				
			} catch (IOException | IllegalArgumentException e) {
				publishProgress(getActivity().getString(R.string.error_connection));
				e.printStackTrace();
			} catch (JSONException e) {
				publishProgress(getActivity().getString(R.string.error_internal_error));
				e.printStackTrace();
			} finally {
				conn.disconnect();
			}
			
			return null;
		}
		
		@Override
		protected void onProgressUpdate(String... values) {
			Toast.makeText(getActivity(), values[0], Toast.LENGTH_SHORT).show();
		}
		
		@Override
		protected void onPostExecute(Void result) {
			cleanScreen();
		}
	}
	
	class CheckOutID extends AsyncTask<Void, String, Void> {

		@Override
		protected Void doInBackground(Void... params) {
			
			HttpURLConnection conn = null;
			try {
				conn = enstablishConnection("PUT", currentID.toString() + "/");
				
				if (currentJSON != null) {
					
					if (currentJSON.getString("check_in").matches("null"))
						publishProgress(getActivity().getString(R.string.error_already_checked_out));
					else {
						currentJSON.put("check_in", JSONObject.NULL);
						
						writeJSON(conn, currentJSON.toString());
						
						if (conn.getResponseCode() == 200) {
							publishProgress(conn.getResponseMessage());
							fetchJSON(conn);
						}
						else
							publishProgress(getActivity().getString(R.string.error_server_code) + "\n" + conn.getResponseCode() + ": " + conn.getResponseMessage());
					}
					
				}
				
			} catch (IOException | IllegalArgumentException e) {
				publishProgress(getActivity().getString(R.string.error_connection));
				e.printStackTrace();
			} catch (JSONException e) {
				publishProgress(getActivity().getString(R.string.error_internal_error));
				e.printStackTrace();
			} finally {
				conn.disconnect();
			}
			
			return null;
		}
		
		@Override
		protected void onProgressUpdate(String... values) {
			Toast.makeText(getActivity(), values[0], Toast.LENGTH_SHORT).show();
		}
		
		@Override
		protected void onPostExecute(Void result) {
			cleanScreen();
		}
	}
}
