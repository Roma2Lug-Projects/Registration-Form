package it.mrmodd.registrationform;

import android.os.Bundle;
import android.preference.PreferenceActivity;

public class ActivitySettings extends PreferenceActivity {
	
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		// Display the fragment as the main content.
        getFragmentManager().beginTransaction()
        	.replace(android.R.id.content, new FragmentSettings())
        	.commit();
	}

}
