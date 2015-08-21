package it.mrmodd.registrationform;

/*************************************************************************\
* Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) *
* on behalf of Roma2LUG (http://lug.uniroma2.it/)                         *
\*************************************************************************/

import it.mrmodd.registrationform.network.NetConnection;

import java.io.IOException;
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
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

public class MainFragment extends Fragment {
	public static final String SERIAL_PATTERN = "[a-z0-9]{16}";
	private Button buttonQR;
	private Button buttonID;
	private Button buttonAccept;
	private Button buttonRemove;
	private Button buttonCancel;
	private Button buttonAssistance;
	
	private TextView textViewCurrentID;
	
	private EditText editTextID;
	
	private String currentID = "";
	private JSONObject currentJSON = null;
	private boolean hasAssistance = false;
	
	
	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		
		View v = inflater.inflate(R.layout.fragment_main, container, false);
		
		buttonQR = (Button) v.findViewById(R.id.button_qr);
		buttonID = (Button) v.findViewById(R.id.button_id);
		buttonAccept = (Button) v.findViewById(R.id.button_accept);
		buttonRemove = (Button) v.findViewById(R.id.button_remove);
		buttonCancel = (Button) v.findViewById(R.id.button_cancel);
		buttonAssistance = (Button) v.findViewById(R.id.button_assistance);
		
		textViewCurrentID = (TextView) v.findViewById(R.id.text_currentID);
		
		editTextID = (EditText) v.findViewById(R.id.editText_id);
		
		buttonQR.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				try {

				    Intent intent = new Intent("com.google.zxing.client.android.SCAN");
				    intent.putExtra("SCAN_MODE", "QR_CODE_MODE"); // "PRODUCT_MODE for bar codes

				    startActivityForResult(intent, 0);

				} catch (android.content.ActivityNotFoundException e) {
					/* Required QR Code app */
					
				    cleanScreen();

					Intent marketIntent = null;
					try {
					    Uri marketUri = Uri.parse("market://details?id=com.google.zxing.client.android");
					    marketIntent = new Intent(Intent.ACTION_VIEW,marketUri);
				    	startActivity(marketIntent);
					} catch (android.content.ActivityNotFoundException e1) {
					    Uri marketUri = Uri.parse("https://play.google.com/store/apps/details?id=com.google.zxing.client.android");
					    marketIntent = new Intent(Intent.ACTION_VIEW,marketUri);
				    	startActivity(marketIntent);
					}
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
				if (!id.matches(SERIAL_PATTERN)) {
					Toast.makeText(getActivity(), R.string.error_invalid_field, Toast.LENGTH_SHORT).show();
					return;
				}
				
				cleanScreen();
				currentID = id;
        		new RetrieveDetails().execute();
				
			}
			
		});
		
		buttonAccept.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				
				if (currentID.length() == 0) {
					Toast.makeText(getActivity(), R.string.error_no_id_selected, Toast.LENGTH_SHORT).show();
					return;
				}
				
				new CheckInID().execute();
			}
			
		});
		
		buttonRemove.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				
				if (currentID.length() == 0) {
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
		
		buttonAssistance.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				
				if (currentID.length() != 0) {
					Intent assistances = new Intent(getActivity(), ActivityAssistances.class);
					assistances.putExtra("id", currentID);
					startActivity(assistances);
				}
				else {
					buttonAssistance.setEnabled(false);
				}
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
	        	if (qr.matches(SERIAL_PATTERN)) {

					cleanScreen();
	        		currentID = qr;
	        		new RetrieveDetails().execute();
	        		
	        	}
	        	else
	        		Toast.makeText(getActivity(), R.string.error_qr_content, Toast.LENGTH_SHORT).show();
	        }
	        if(resultCode == Activity.RESULT_CANCELED){
	            // There's nothing to do
	        }
	    }
	}
	
	private void cleanScreen() {
		currentID = "";
		currentJSON = null;
		textViewCurrentID.setText(R.string.text_empty);
		editTextID.setText("");
		buttonAssistance.setEnabled(false);
		buttonAssistance.setText(R.string.button_assistance_def);
		hasAssistance = false;
	}
	
	class RetrieveDetails extends AsyncTask<Void, String, String> {

		@Override
		protected String doInBackground(Void... params) {
			String newtext = null;
			NetConnection conn = null;

			SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(getActivity());
			String server = pref.getString(getActivity().getString(R.string.pref_key_server_url), "");
			String user = pref.getString(getActivity().getString(R.string.pref_key_username), "");
			String pass = pref.getString(getActivity().getString(R.string.pref_key_password), "");
			
			if (!server.endsWith("/"))
				server += "/";
			
			try {
				
				conn = new NetConnection("GET", server + NetConnection.PARTICIPANTS_PATH + currentID + "/");
				conn.setCredential(user, pass);
				
				if (conn.getResponseCode() == 200) {
					
					String json = conn.readString();

					//Parse JSON
					currentJSON = new JSONObject(json);
					
					String first_name = currentJSON.getString("first_name");
					String last_name = currentJSON.getString("last_name");
					String email = currentJSON.getString("email");
					Boolean morning = currentJSON.getBoolean("participate_morning");
					Boolean afternoon = currentJSON.getBoolean("participate_afternoon");
					String checkin = (!currentJSON.getString("check_in").matches("null")) ? currentJSON.getString("check_in") : "--";
					String comments = currentJSON.getString("comments");

					newtext = getActivity().getString(R.string.text_currentID) + " " + currentID + "\n";
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
			
			// Check if this ID has an assistance
			try {
				
				conn = new NetConnection("HEAD", server + NetConnection.ASSISTANCES_PATH + currentID + "/");
				conn.setCredential(user, pass);
				
				if (conn.getResponseCode() == 200) {
					hasAssistance = true;
				}
				
			} catch (IOException | IllegalArgumentException e) {
				publishProgress(getActivity().getString(R.string.error_connection));
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
			if (hasAssistance) {
				buttonAssistance.setEnabled(true);
				buttonAssistance.setText(R.string.button_assistance);
			}
		}
	}
	
	class CheckInID extends AsyncTask<Void, String, Void> {

		@Override
		protected Void doInBackground(Void... params) {
			NetConnection conn = null;

			SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(getActivity());
			String server = pref.getString(getActivity().getString(R.string.pref_key_server_url), "");
			String user = pref.getString(getActivity().getString(R.string.pref_key_username), "");
			String pass = pref.getString(getActivity().getString(R.string.pref_key_password), "");
			
			if (!server.endsWith("/"))
				server += "/";
			
			try {
				conn = new NetConnection("PUT", server + NetConnection.PARTICIPANTS_PATH + currentID + "/");
				conn.setCredential(user, pass);
				
				if (currentJSON != null) {
					if (!currentJSON.getString("check_in").matches("null"))
						publishProgress(getActivity().getString(R.string.error_already_checked_in));
					else {
						String date = new java.sql.Timestamp(new Date().getTime()).toString();
						currentJSON.put("check_in", date);
						
						conn.writeString(currentJSON.toString());
						
						if (conn.getResponseCode() == 200) {
							publishProgress(conn.getResponseMessage());
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
			NetConnection conn = null;

			SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(getActivity());
			String server = pref.getString(getActivity().getString(R.string.pref_key_server_url), "");
			String user = pref.getString(getActivity().getString(R.string.pref_key_username), "");
			String pass = pref.getString(getActivity().getString(R.string.pref_key_password), "");
			
			if (!server.endsWith("/"))
				server += "/";
			
			try {
				conn = new NetConnection("PUT", server + NetConnection.PARTICIPANTS_PATH + currentID + "/");
				conn.setCredential(user, pass);
				
				if (currentJSON != null) {
					
					if (currentJSON.getString("check_in").matches("null"))
						publishProgress(getActivity().getString(R.string.error_already_checked_out));
					else {
						currentJSON.put("check_in", JSONObject.NULL);
						
						conn.writeString(currentJSON.toString());
						
						if (conn.getResponseCode() == 200) {
							publishProgress(conn.getResponseMessage());
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
