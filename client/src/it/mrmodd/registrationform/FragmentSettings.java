package it.mrmodd.registrationform;

import java.io.File;

import android.os.Bundle;
import android.preference.ListPreference;
import android.preference.Preference;
import android.preference.PreferenceFragment;
import android.preference.PreferenceManager;

public class FragmentSettings extends PreferenceFragment {

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		addPreferencesFromResource(R.xml.settings);

		bindPreferenceSummaryToValue(findPreference(getString(R.string.pref_key_server_url)));
		
	}
	
	/**
	 * A preference value change listener that updates the preference's summary
	 * to reflect its new value.
	 */
	private static Preference.OnPreferenceChangeListener sBindPreferenceSummaryToValueListener = new Preference.OnPreferenceChangeListener() {
		@Override
		public boolean onPreferenceChange(Preference preference, Object value) {
			String stringValue = value.toString();

			if (preference instanceof ListPreference) {
				// For list preferences, look up the correct display value in
				// the preference's 'entries' list.
				ListPreference listPreference = (ListPreference) preference;
				int index = listPreference.findIndexOfValue(stringValue);

				// Set the summary to reflect the new value.
				preference.setSummary(index >= 0 ? listPreference.getEntries()[index] : null);

			} else {
				// For all other preferences, set the summary to the value's
				// simple string representation.
				preference.setSummary(stringValue);
			}
			return true;
		}
	};

	/**
	 * Binds a preference's summary to its value. More specifically, when the
	 * preference's value is changed, its summary (line of text below the
	 * preference title) is updated to reflect the value. The summary is also
	 * immediately updated upon calling this method. The exact display format is
	 * dependent on the type of preference.
	 * 
	 * @see #sBindPreferenceSummaryToValueListener
	 */
	private static void bindPreferenceSummaryToValue(Preference preference) {
		// Set the listener to watch for value changes.
		preference.setOnPreferenceChangeListener(sBindPreferenceSummaryToValueListener);

		// Trigger the listener immediately with the preference's
		// current value.
		sBindPreferenceSummaryToValueListener.onPreferenceChange(
				preference,
				PreferenceManager.getDefaultSharedPreferences(
						preference.getContext()).getString(preference.getKey(),
						""));
	}
	
	/**
	 * Obtain the dimension of a directory and all included files
	 * @param f File descriptor of a directory
	 * @return recursive dimension in bytes of all files contained in f
	 */
	public static long pathSize(File f) {
		if (f == null || !f.exists())
			return 0;
		if (f.isFile())
			return f.length();
	    long length = 0;
	    for (File file : f.listFiles()) {
	        if (file.isFile())
	            length += file.length();
	        else
	            length += pathSize(file);
	    }
	    return length;
	}
	
	/**
	 * Delete recursively a directory
	 * @param file File descriptor of a directory
	 */
	public static void deleteDirectory(File file) {
		if(file.isDirectory()){
			//directory is empty, then delete it
			if(file.list().length == 0){
				file.delete();
			} else {
				//list all the directory contents
				String files[] = file.list();
 
				for (String temp : files) {
					//construct the file structure
					File fileDelete = new File(file, temp);
 
					//recursive delete
					deleteDirectory(fileDelete);
				}
				//check the directory again, if empty then delete it
				if(file.list().length == 0){
					file.delete();
				}
			}
		} else {
			//if file, then delete it
			file.delete();
		}
	} 

}
