package it.mrmodd.registrationform;

import android.app.Fragment;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
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
		
		return v;
	}
}
