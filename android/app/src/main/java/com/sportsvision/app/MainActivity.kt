package com.sportsvision.app

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup
import android.webkit.*
import android.widget.FrameLayout
import android.widget.ProgressBar
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var loader: ProgressBar
    private var fileChooserCallback: ValueCallback<Array<Uri>>? = null

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

        // Layout raíz con fondo oscuro
        val root = FrameLayout(this).apply {
            setBackgroundColor(Color.parseColor("#0b0c18"))
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }

        // WebView
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
            }
        }

        // Spinner de carga centrado
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

        // Habilitar cookies — necesario para que Django valide el token CSRF en formularios POST
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
                return if (url.startsWith("https://web-production-f0f4b.up.railway.app")) {
                    false
                } else {
                    startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                    true
                }
            }

            override fun onPageFinished(view: WebView, url: String) {
                loader.visibility = android.view.View.GONE
            }

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
                      <button onclick="window.location.href='https://web-production-f0f4b.up.railway.app'"
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

        webView.loadUrl("https://web-production-f0f4b.up.railway.app")

        // Botón atrás del sistema (reemplaza onBackPressed() obsoleto en API 33+)
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
