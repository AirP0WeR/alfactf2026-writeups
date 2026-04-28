.class Lio/peakmood/mobile/MainActivity$3;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity;->configureButtons()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lio/peakmood/mobile/MainActivity;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010
        }
        names = {
            null
        }
    .end annotation

    .line 171
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$3;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 0

    .line 174
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity$3;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {p1}, Lio/peakmood/mobile/MainActivity;->access$300(Lio/peakmood/mobile/MainActivity;)V

    .line 175
    return-void
.end method
