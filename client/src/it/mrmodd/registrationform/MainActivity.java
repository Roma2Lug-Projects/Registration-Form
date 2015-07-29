package it.mrmodd.registrationform;

/*************************************************************************\
* Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) *
* on behalf of Roma2LUG (http://lug.uniroma2.it/)                         *
\*************************************************************************/

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;

public class MainActivity extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		
		// Display the fragment as the main content.
        getFragmentManager().beginTransaction()
        	.replace(R.id.activity_main_container, new MainFragment())
        	.commit();
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// Handle action bar item clicks here. The action bar will
		// automatically handle clicks on the Home/Up button, so long
		// as you specify a parent activity in AndroidManifest.xml.
		int id = item.getItemId();
		if (id == R.id.action_settings) {
			startActivity(new Intent(this, ActivitySettings.class));
			return true;
		}
		return super.onOptionsItemSelected(item);
	}
}
