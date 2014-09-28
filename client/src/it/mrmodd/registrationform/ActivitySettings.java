package it.mrmodd.registrationform;

/********************************************************************\
* Copyright (C) 2014 Federico "MrModd" Cosentino (http://mrmodd.it/) *
* on behalf of Roma2LUG (http://lug.uniroma2.it/)                    *
\********************************************************************/

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
