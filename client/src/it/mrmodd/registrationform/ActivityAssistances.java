package it.mrmodd.registrationform;

import android.app.Activity;
import android.os.Bundle;

public class ActivityAssistances extends Activity {
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_empty);
		
		// Display the fragment as the main content.
        getFragmentManager().beginTransaction()
        	.replace(R.id.activity_main_container, new FragmentAssistances())
        	.commit();
	}
}
