package com.vesper.firstblood;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceError;
import android.util.Log;

/** Offline WebView shell. The whole game and sprite atlas are inside APK assets.
 * Nothing is fetched from a server. Hardware acceleration is enabled for canvas. */
public class MainActivity extends Activity {
    private WebView game;
    @SuppressLint("SetJavaScriptEnabled")
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().getDecorView().setSystemUiVisibility(
          View.SYSTEM_UI_FLAG_FULLSCREEN |
          View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
          View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
          View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
          View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
          View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        game=new WebView(this);
        game.setLayerType(View.LAYER_TYPE_HARDWARE, null);
        game.setBackgroundColor(0xFF050610);
        game.setOverScrollMode(View.OVER_SCROLL_NEVER);
        game.setVerticalScrollBarEnabled(false);
        game.setHorizontalScrollBarEnabled(false);
        WebSettings opts=game.getSettings();
        opts.setJavaScriptEnabled(true);
        opts.setDomStorageEnabled(true);
        opts.setAllowFileAccess(true);
        opts.setAllowContentAccess(false);
        opts.setMediaPlaybackRequiresUserGesture(false);
        opts.setDefaultTextEncodingName("UTF-8");
        // No remote URLs and no external navigation in the app.
        game.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !"file".equalsIgnoreCase(request.getUrl().getScheme());
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest req, WebResourceError err) {
                Log.e("Vesper", "Offline asset failed: " + req.getUrl() + " " + err.getDescription());
            }
        });
        game.setWebChromeClient(new WebChromeClient());
        setContentView(game);
        game.loadUrl("file:///android_asset/index.html");
    }
    @Override public void onBackPressed() {
        if (game != null) {
            // Escape shortcut toggles in-game pause and lets players exit to main menu.
            game.evaluateJavascript("window.dispatchEvent(new KeyboardEvent('keydown',{code:'Escape',key:'Escape',bubbles:true}))", null);
        } else super.onBackPressed();
    }
    @Override protected void onDestroy() {
        if(game!=null){game.loadUrl("about:blank");game.destroy();game=null;}
        super.onDestroy();
    }
}
