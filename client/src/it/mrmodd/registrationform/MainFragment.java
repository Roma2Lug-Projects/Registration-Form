package it.mrmodd.registrationform;

import android.app.Activity;
import android.app.Fragment;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class MainFragment extends Fragment {
	private Button buttonQR;
	private Button buttonID;
	private Button buttonName;
	private Button buttonAccept;
	private Button buttonCancel;
	
	private TextView textViewCurrentID;
	
	private EditText editTextID;
	private EditText editTextName;
	
	
	
	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		
		View v = inflater.inflate(R.layout.fragment_main, container, false);
		
		buttonQR = (Button) v.findViewById(R.id.button_qr);
		buttonID = (Button) v.findViewById(R.id.button_id);
		buttonName = (Button) v.findViewById(R.id.button_name);
		buttonAccept = (Button) v.findViewById(R.id.button_accept);
		buttonCancel = (Button) v.findViewById(R.id.button_cancel);
		
		textViewCurrentID = (TextView) v.findViewById(R.id.text_currentID);
		
		editTextID = (EditText) v.findViewById(R.id.editText_id);
		editTextName = (EditText) v.findViewById(R.id.editText_name);
		
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
				    startActivity(marketIntent);

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
	        	textViewCurrentID.setText(getActivity().getString(R.string.text_currentID) + " " + data.getStringExtra("SCAN_RESULT"));
	        }
	        if(resultCode == Activity.RESULT_CANCELED){
	            //handle cancel
	        }
	    }
	}
}
