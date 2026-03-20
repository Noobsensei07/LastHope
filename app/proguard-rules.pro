# Flutter Wrapper
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Dart Native Extensions
-keep class io.flutter.embedding.** { *; }
-keep class io.flutter.embedding.engine.** { *; }

# GeoLocator & Sensors
-keep class com.baseflow.geolocator.** { *; }
-keep class dev.fluttercommunity.plus.sensors.** { *; }
-keep class dev.fluttercommunity.plus.** { *; }

# Permission Handler
-keep class com.baseflow.permissionhandler.** { *; }

# Firebase Core & Analytics
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.android.gms.**

# Firebase Firestore - Critical for data model serialization
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes EnclosingMethod
-keepattributes InnerClasses

# Keep all Firestore model classes and their fields
-keep class * extends com.google.firebase.firestore.** { *; }
-keepclassmembers class * {
    @com.google.firebase.firestore.PropertyName <fields>;
}

# Firebase Auth
-keep class com.google.firebase.auth.** { *; }

# Nearby Connections
-keep class com.pkmnapps.nearby_connections.** { *; }
-keep class com.google.android.gms.nearby.** { *; }

# Background Service
-keep class id.flutter.flutter_background_service.** { *; }

# Wakelock
-keep class creativemaybeno.wakelock.** { *; }

# URL Launcher
-keep class io.flutter.plugins.urllauncher.** { *; }

# WebSocket Channel
-keep class dev.fluttercommunity.plus.** { *; }

# Notifications
-keep class com.dexterous.flutterlocalnotifications.** { *; }

# Google Play Services Split Install
-dontwarn com.google.android.play.core.splitcompat.**
-dontwarn com.google.android.play.core.splitinstall.**
-dontwarn com.google.android.play.core.tasks.**
-keep class com.google.android.play.core.splitcompat.** { *; }
-keep class com.google.android.play.core.splitinstall.** { *; }

# Prevent obfuscation of model classes with toMap/fromMap
-keepclassmembers class * {
    public <init>(...);
    public static *** fromMap(...);
    public *** toMap();
}

# Keep all classes with serialization methods
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    !static !transient <fields>;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

# Gson (if used by Firebase or other libraries)
-keepattributes Signature
-keep class sun.misc.Unsafe { *; }
-keep class com.google.gson.** { *; }

# Prevent stripping of native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep enums
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# CRITICAL: Prevent R8 from stripping Services and Receivers in Release mode
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.app.IntentService

# Additional Firebase plugin protection
-keep class io.flutter.plugins.firebase.** { *; }

