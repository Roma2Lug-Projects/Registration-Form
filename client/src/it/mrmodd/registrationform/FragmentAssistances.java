package it.mrmodd.registrationform;

import it.mrmodd.registrationform.network.NetConnection;

import java.io.IOException;

import org.json.JSONException;
import org.json.JSONObject;

import android.app.Fragment;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

public class FragmentAssistances extends Fragment {
	String currentID = null;
	
	TextView viewID;
	ProgressBar progress;
	TextView viewDetails;
	Button buttonTake;
	
	JSONObject currentJSON = null;
	
	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		
		View v = inflater.inflate(R.layout.fragment_assistances, container, false);
		
		viewID = (TextView) v.findViewById(R.id.text_id);
		progress = (ProgressBar) v.findViewById(R.id.progressBar);
		viewDetails = (TextView) v.findViewById(R.id.text_details);
		buttonTake = (Button) v.findViewById(R.id.button_take);
		
		Intent i = getActivity().getIntent();
		currentID = i.getExtras().getString("id");
		
		viewID.setText("ID: " + currentID);
		
		buttonTake.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				
				new TakeAssistance().execute();
				
			}
			
		});
		
		new RetrieveDetails().execute();
		
		return v;
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
				
				conn = new NetConnection("GET", server + NetConnection.ASSISTANCES_PATH + currentID + "/");
				conn.setCredential(user, pass);
				
				if (conn.getResponseCode() == 200) {
					
					String json = conn.readString();

					//Parse JSON
					currentJSON = new JSONObject(json);
					
					String pc_type = currentJSON.getString("pc_type");
					
					if (pc_type.equals("dt"))
						pc_type = getActivity().getString(R.string.text_desktop);
					else if (pc_type.equals("lt"))
						pc_type = getActivity().getString(R.string.text_laptop);
					else if (pc_type.equals("cb"))
						pc_type = getActivity().getString(R.string.text_chromebook);
					else if (pc_type.equals("tf"))
						pc_type = getActivity().getString(R.string.text_transformer);
					else if (pc_type.equals("oo"))
						pc_type = getActivity().getString(R.string.text_pc_other);
					
					String brand = currentJSON.getString("brand");
					String model = currentJSON.getString("model");
					String cpu = currentJSON.getString("cpu");
					String ram = currentJSON.getString("ram");
					String problem = currentJSON.getString("problem");
					String acceptance = (currentJSON.getString("acceptance").matches("0")) ? getActivity().getString(R.string.text_refused) : getActivity().getString(R.string.text_accepted);
					String accepted_time = (!currentJSON.getString("accepted_time").matches("null")) ? currentJSON.getString("accepted_time") : "";
					String estimated_mttr = (!currentJSON.getString("estimated_mttr").matches("null")) ? currentJSON.getString("estimated_mttr") : "";
					String operator = (!currentJSON.getString("operator").matches("null")) ? currentJSON.getString("operator") : "--";
					
					newtext = getActivity().getString(R.string.text_pctype) + " " + pc_type + "\n";
					newtext += getActivity().getString(R.string.text_brand) + " " + brand + "\n";
					newtext += getActivity().getString(R.string.text_model) + " " + model + "\n";
					newtext += getActivity().getString(R.string.text_cpu) + " " + cpu + "\n";
					newtext += getActivity().getString(R.string.text_ram) + " " + ram + "\n";
					newtext += getActivity().getString(R.string.text_problem) + " " + problem + "\n";
					newtext += getActivity().getString(R.string.text_acceptance) + " " + acceptance + "\n";
					newtext += getActivity().getString(R.string.text_accepted_time) + " " + accepted_time + "\n";
					newtext += getActivity().getString(R.string.text_mttr) + " " + estimated_mttr + "\n";
					newtext += getActivity().getString(R.string.text_operator) + " " + operator + "\n";
		            
				}
				else {
					publishProgress(getActivity().getString(R.string.error_server_code) + "\n" + conn.getResponseCode() + ": " + conn.getResponseMessage());
				}
				
			} catch (IOException | IllegalArgumentException e) {
				Log.e("FragmentAssistances", "Connection error: " + e.getMessage());
				if (getActivity() != null)
					publishProgress(getActivity().getString(R.string.error_connection));
			} catch (JSONException e) {
				Log.e("FragmentAssistances", "Error parsing JSON response: " + e.getMessage());
				if (getActivity() != null)
					publishProgress(getActivity().getString(R.string.error_invalid_response));
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
			if (result != null) {
				viewDetails.setText(result);
				progress.setVisibility(View.INVISIBLE);
			}
		}
	}
	
	class TakeAssistance extends AsyncTask<Void, String, Void> {

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
				conn = new NetConnection("PUT", server + NetConnection.ASSISTANCES_PATH + currentID + "/");
				conn.setCredential(user, pass);
				
				if (currentJSON != null) {
					if (!currentJSON.getString("operator").matches("null") && currentJSON.getString("operator").length() > 0)
						publishProgress(getActivity().getString(R.string.error_already_taken));
					else {
						currentJSON.put("operator", user);
						
						conn.writeString(currentJSON.toString());
						
						if (conn.getResponseCode() == 200) {
							publishProgress(conn.getResponseMessage());
						}
						else
							publishProgress(getActivity().getString(R.string.error_server_code) + "\n" + conn.getResponseCode() + ": " + conn.getResponseMessage());
					}
				}
				
			} catch (IOException | IllegalArgumentException e) {
				Log.e("FragmentAssistances", "Connection error: " + e.getMessage());
				if (getActivity() != null)
					publishProgress(getActivity().getString(R.string.error_connection));
			} catch (JSONException e) {
				Log.e("FragmentAssistances", "Error parsing JSON response: " + e.getMessage());
				if (getActivity() != null)
					publishProgress(getActivity().getString(R.string.error_internal_error));
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
			new RetrieveDetails().execute();
		}
	}
}
