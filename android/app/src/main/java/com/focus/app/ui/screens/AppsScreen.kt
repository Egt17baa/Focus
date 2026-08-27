package com.focus.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.focus.app.data.BlockedApp

@Composable
fun AppsScreen(
    apps: List<BlockedApp>,
    onAdd: (String, String?) -> Unit,
    onRemove: (Int) -> Unit,
) {
    var name by remember { mutableStateOf("") }
    var packageName by remember { mutableStateOf("") }

    LazyColumn(
        modifier = Modifier.fillMaxWidth().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text("Apps que te distraen", style = MaterialTheme.typography.titleMedium)
        }
        item {
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text("Nombre (Instagram)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            OutlinedTextField(
                value = packageName,
                onValueChange = { packageName = it },
                label = { Text("Paquete (com.instagram.android)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            Button(
                onClick = {
                    onAdd(name, packageName.ifBlank { null })
                    name = ""
                    packageName = ""
                },
                enabled = name.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Añadir a la lista de bloqueo")
            }
        }
        items(apps) { app ->
            Card(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.padding(12.dp).fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(app.appName, style = MaterialTheme.typography.titleSmall)
                        Text(
                            app.packageName ?: "sin paquete",
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                    IconButton(onClick = { onRemove(app.id) }) {
                        Icon(Icons.Default.Delete, contentDescription = "Eliminar ${app.appName}")
                    }
                }
            }
        }
    }
}
