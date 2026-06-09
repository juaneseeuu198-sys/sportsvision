package com.sportsvision.app

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.app.DownloadManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.view.Gravity
import android.view.ViewGroup
import android.webkit.*
import android.widget.FrameLayout
import android.widget.ProgressBar
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.browser.customtabs.CustomTabsIntent
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import org.json.JSONObject
import java.io.File
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var loader: ProgressBar
    private var fileChooserCallback: ValueCallback<Array<Uri>>? = null

    companion object {
        private const val BASE_URL = "https://web-production-f0f4b.up.railway.app"
        private const val GOOGLE_LOGIN_PATH = "/usuarios/auth/google/"
        private const val CURRENT_VERSION_CODE = 2  // Cambiar al compilar nueva versión
    }

    private var downloadId: Long = -1

    private val permisos: Array<String>
        get() = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(Manifest.permission.READ_MEDIA_IMAGES, Manifest.permission.CAMERA)
        } else {
            arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.CAMERA)
        }

    private val galeriaLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val uris: Array<Uri>? = if (result.resultCode == Activity.RESULT_OK) {
            result.data?.data?.let { arrayOf(it) }
        } else null
        fileChooserCallback?.onReceiveValue(uris ?: emptyArray())
        fileChooserCallback = null
    }

    private val permisosLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { resultados ->
        val todosConcedidos = resultados.values.any { it }
        if (todosConcedidos) {
            abrirSelectorImagen()
        } else {
            Toast.makeText(
                this,
                "Permiso denegado. Ve a Ajustes > Aplicaciones > SportsVision > Permisos.",
                Toast.LENGTH_LONG
            ).show()
            fileChooserCallback?.onReceiveValue(emptyArray())
            fileChooserCallback = null
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val root = FrameLayout(this).apply {
            setBackgroundColor(Color.parseColor("#0b0c18"))
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }

        webView = WebView(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#0b0c18"))
            settings.apply {
                javaScriptEnabled      = true
                domStorageEnabled      = true
                allowFileAccess        = true
                allowContentAccess     = true
                useWideViewPort        = true
                loadWithOverviewMode   = true
                setSupportZoom(false)
                builtInZoomControls    = false
                displayZoomControls    = false
                cacheMode              = android.webkit.WebSettings.LOAD_NO_CACHE
            }
            clearCache(true)
        }

        loader = ProgressBar(this).apply {
            isIndeterminate = true
            indeterminateTintList = android.content.res.ColorStateList.valueOf(
                Color.parseColor("#7b2ff7")
            )
            layoutParams = FrameLayout.LayoutParams(120, 120, Gravity.CENTER)
        }

        root.addView(webView)
        root.addView(loader)
        setContentView(root)

        CookieManager.getInstance().apply {
            setAcceptCookie(true)
            setAcceptThirdPartyCookies(webView, true)
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView,
                request: WebResourceRequest
            ): Boolean {
                val url = request.url.toString()

                // Google OAuth → abrir en Chrome Custom Tabs con flag ?from=app
                if (url.startsWith("$BASE_URL$GOOGLE_LOGIN_PATH") ||
                    url.contains("accounts.google.com")) {
                    val targetUrl = if (url.startsWith("$BASE_URL$GOOGLE_LOGIN_PATH") &&
                                        !url.contains("from=app")) {
                        if (url.contains("?")) "$url&from=app" else "$url?from=app"
                    } else url
                    abrirCustomTabs(targetUrl)
                    return true
                }

                // URLs de nuestra app → cargar en WebView
                return if (url.startsWith(BASE_URL)) {
                    false
                } else {
                    // Otros enlaces externos → navegador del sistema
                    startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                    true
                }
            }

            override fun onPageFinished(view: WebView, url: String) {
                loader.visibility = android.view.View.GONE
            }

            @Suppress("OVERRIDE_DEPRECATION")
            override fun onReceivedError(
                view: WebView,
                errorCode: Int,
                description: String,
                failingUrl: String
            ) {
                loader.visibility = android.view.View.GONE
                view.loadData(
                    """
                    <html><body style="background:#0b0c18;color:#fff;font-family:sans-serif;
                                      display:flex;flex-direction:column;align-items:center;
                                      justify-content:center;height:100vh;margin:0;
                                      text-align:center;padding:24px;">
                      <div style="font-size:48px;">📡</div>
                      <h2 style="color:#7b2ff7;margin:16px 0 8px;">Sin conexión</h2>
                      <p style="color:#aaa;line-height:1.6;">
                        No se pudo conectar a SportsVision.<br>
                        Verifica tu conexión a internet.
                      </p>
                      <button onclick="window.location.href='$BASE_URL'"
                        style="margin-top:20px;background:#7b2ff7;color:#fff;border:none;
                               border-radius:12px;padding:14px 32px;font-size:16px;cursor:pointer;">
                        Reintentar
                      </button>
                    </body></html>
                    """.trimIndent(),
                    "text/html", "UTF-8"
                )
            }
        }

        // Manejar descargas (PDF, APK, etc.) desde el WebView
        webView.setDownloadListener { url, userAgent, contentDisposition, mimetype, _ ->
            try {
                val request = DownloadManager.Request(Uri.parse(url)).apply {
                    setMimeType(mimetype)
                    addRequestHeader("Cookie", CookieManager.getInstance().getCookie(url))
                    addRequestHeader("User-Agent", userAgent)
                    setDescription("Descargando archivo...")
                    setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    setDestinationInExternalPublicDir(
                        Environment.DIRECTORY_DOWNLOADS,
                        android.webkit.URLUtil.guessFileName(url, contentDisposition, mimetype)
                    )
                }
                val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
                dm.enqueue(request)
                Toast.makeText(this, "Descargando PDF...", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                // Fallback: abrir en navegador
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                fileChooserCallback?.onReceiveValue(emptyArray())
                fileChooserCallback = filePathCallback
                solicitarPermisosYAbrir()
                return true
            }
        }

        // Manejar deep link si la app se abrió desde sportsvision://auth?token=...
        intent?.data?.let { manejarDeepLink(it) } ?: webView.loadUrl(BASE_URL)

        // Verificar actualizaciones al iniciar
        verificarActualizacion()

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
    }

    // Recibe deep links cuando la app ya está abierta (launchMode=singleTask)
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        intent.data?.let { manejarDeepLink(it) }
    }

    private fun manejarDeepLink(uri: Uri) {
        if (uri.scheme == "sportsvision" && uri.host == "auth") {
            val token = uri.getQueryParameter("token")
            if (!token.isNullOrEmpty()) {
                // Cargar la URL de validación del token directamente en el WebView
                loader.visibility = android.view.View.VISIBLE
                webView.loadUrl("$BASE_URL/usuarios/auth/mobile/?token=$token")
            } else {
                webView.loadUrl(BASE_URL)
            }
        } else {
            webView.loadUrl(BASE_URL)
        }
    }

    private fun verificarActualizacion() {
        thread {
            try {
                val json = URL("$BASE_URL/api/version/").readText()
                val obj = JSONObject(json)
                val serverVersion = obj.getInt("version_code")
                val versionName = obj.getString("version_name")
                val apkUrl = obj.getString("apk_url")

                if (serverVersion > CURRENT_VERSION_CODE) {
                    runOnUiThread {
                        AlertDialog.Builder(this)
                            .setTitle("Nueva versión disponible")
                            .setMessage("Versión $versionName disponible. ¿Deseas actualizar ahora?")
                            .setPositiveButton("Actualizar") { _, _ ->
                                descargarEInstalar(apkUrl, versionName)
                            }
                            .setNegativeButton("Después", null)
                            .show()
                    }
                }
            } catch (e: Exception) {
                // Sin conexión o error — ignorar
            }
        }
    }

    private fun descargarEInstalar(apkUrl: String, versionName: String) {
        val fileName = "SportsVision-$versionName.apk"

        val request = DownloadManager.Request(Uri.parse(apkUrl)).apply {
            setTitle("SportsVision $versionName")
            setDescription("Descargando actualización...")
            setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            setDestinationInExternalFilesDir(
                this@MainActivity, Environment.DIRECTORY_DOWNLOADS, fileName
            )
        }

        val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        downloadId = dm.enqueue(request)

        val receiver = object : BroadcastReceiver() {
            override fun onReceive(ctx: Context, intent: Intent) {
                val id = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1)
                if (id != downloadId) return
                try { unregisterReceiver(this) } catch (_: Exception) {}
                val apkFile = File(
                    getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), fileName
                )
                if (apkFile.exists()) instalarApk(apkFile)
            }
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(receiver, IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE), RECEIVER_NOT_EXPORTED)
        } else {
            @Suppress("UnspecifiedRegisterReceiverFlag")
            registerReceiver(receiver, IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE))
        }
        Toast.makeText(this, "Descargando actualización...", Toast.LENGTH_SHORT).show()
    }

    private fun instalarApk(apkFile: File) {
        val uri = FileProvider.getUriForFile(this, "com.sportsvision.app.fileprovider", apkFile)
        val install = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        startActivity(install)
    }

    private fun abrirCustomTabs(url: String) {
        val customTabsIntent = CustomTabsIntent.Builder()
            .setShowTitle(true)
            .build()
        customTabsIntent.launchUrl(this, Uri.parse(url))
    }

    private fun solicitarPermisosYAbrir() {
        val faltantes = permisos.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }.toTypedArray()

        if (faltantes.isEmpty()) {
            abrirSelectorImagen()
        } else {
            permisosLauncher.launch(faltantes)
        }
    }

    private fun abrirSelectorImagen() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "image/*"
            putExtra(Intent.EXTRA_ALLOW_MULTIPLE, false)
        }
        galeriaLauncher.launch(Intent.createChooser(intent, "Seleccionar foto"))
    }
}
