package com.focus.app.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "focus_auth")

/** Persists the JWT pair issued by the Focus API. */
class TokenStore(private val context: Context) {
    private val accessKey = stringPreferencesKey("access_token")
    private val refreshKey = stringPreferencesKey("refresh_token")

    suspend fun access(): String? = context.dataStore.data.first()[accessKey]

    suspend fun refresh(): String? = context.dataStore.data.first()[refreshKey]

    suspend fun save(access: String, refresh: String) {
        context.dataStore.edit {
            it[accessKey] = access
            it[refreshKey] = refresh
        }
    }

    suspend fun saveAccess(access: String) {
        context.dataStore.edit { it[accessKey] = access }
    }

    suspend fun clear() {
        context.dataStore.edit { it.clear() }
    }
}
