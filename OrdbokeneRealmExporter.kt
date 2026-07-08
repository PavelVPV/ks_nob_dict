/*
 Dynamic Realm JSON exporter for the Ordbøkene APK database.

 Status: this is the practical next-step exporter. It must run in an Android/JVM
 environment where Realm Java is available. It uses DynamicRealm, so it does not
 need the app's generated Realm proxy classes.

 Input file from APK:
   assets/database/ordboken.realm_109nn_88nb.zip -> ordboken.realm

 Main classes detected in the database:
   WordEntry, Headword, WordSenseGroup, WordSenseEntry, Inflection, WordGram,
   Etymology, Reference, InflectionTableRow
*/

import io.realm.DynamicRealm
import io.realm.DynamicRealmObject
import io.realm.RealmConfiguration
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

object OrdbokeneRealmExporter {
    fun export(realmFile: File, outputFile: File, schemaVersion: Long = 0L, limit: Long = Long.MAX_VALUE) {
        val config = RealmConfiguration.Builder()
            .directory(realmFile.parentFile!!)
            .name(realmFile.name)
            .readOnly()
            .schemaVersion(schemaVersion)
            .build()

        val realm = DynamicRealm.getInstance(config)
        val out = JSONArray()
        try {
            val entries = realm.where("WordEntry").findAll()
            val n = minOf(entries.size.toLong(), limit).toInt()
            for (i in 0 until n) {
                val e = entries[i] ?: continue
                val obj = JSONObject()
                putIfPresent(e, obj, "id")
                putIfPresent(e, obj, "entryTypeRaw")
                putIfPresent(e, obj, "entrySubTypeRaw")
                putIfPresent(e, obj, "partOfSpeechGroupId")

                obj.put("headwords", exportList(e, "headwords", arrayOf("headword", "sortingText", "language")))
                obj.put("grams", exportList(e, "grams", arrayOf("full", "abbreviated", "wordGramId")))
                obj.put("inflections", exportList(e, "inflections", arrayOf("inflectionText", "inflection", "inflectionHitCount")))
                obj.put("senseGroups", exportSenseGroups(e))
                obj.put("etymology", exportList(e, "etymology", arrayOf("definition", "flattenedNodeText", "etymologyTypeRaw")))
                out.put(obj)
            }
        } finally {
            realm.close()
        }
        outputFile.writeText(out.toString(2), Charsets.UTF_8)
    }

    private fun exportSenseGroups(e: DynamicRealmObject): JSONArray {
        val arr = JSONArray()
        if (!hasField(e, "senseGroups")) return arr
        e.getList("senseGroups")?.forEach { g -> arr.put(exportSenseGroup(g)) }
        return arr
    }

    private fun exportSenseGroup(g: DynamicRealmObject): JSONObject {
        val o = JSONObject()
        putIfPresent(g, o, "definition")
        putIfPresent(g, o, "flattenedNodeText")
        putIfPresent(g, o, "number")
        putIfPresent(g, o, "romanNumeral")
        putIfPresent(g, o, "isCrossReference")
        if (hasField(g, "childGroups")) {
            val children = JSONArray()
            g.getList("childGroups")?.forEach { child -> children.put(exportSenseGroup(child)) }
            o.put("childGroups", children)
        }
        return o
    }

    private fun exportList(parent: DynamicRealmObject, field: String, fields: Array<String>): JSONArray {
        val arr = JSONArray()
        if (!hasField(parent, field)) return arr
        parent.getList(field)?.forEach { child ->
            val o = JSONObject()
            fields.forEach { putIfPresent(child, o, it) }
            arr.put(o)
        }
        return arr
    }

    private fun putIfPresent(obj: DynamicRealmObject, out: JSONObject, field: String) {
        if (!hasField(obj, field)) return
        try {
            val value = when (obj.getFieldType(field).name) {
                "STRING" -> obj.getString(field)
                "INTEGER" -> obj.getLong(field)
                "BOOLEAN" -> obj.getBoolean(field)
                "DATE" -> obj.getDate(field)?.toString()
                else -> null
            }
            if (value != null) out.put(field, value)
        } catch (_: Throwable) {
            // Field exists but has an unsupported type in this generic exporter.
        }
    }

    private fun hasField(obj: DynamicRealmObject, field: String): Boolean {
        return try { obj.getFieldType(field); true } catch (_: Throwable) { false }
    }
}
