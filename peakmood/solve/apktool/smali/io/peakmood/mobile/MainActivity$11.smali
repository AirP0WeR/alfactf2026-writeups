.class Lio/peakmood/mobile/MainActivity$11;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity;->showReconnectDialog()V
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

    .line 825
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$11;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .locals 0

    .line 828
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity$11;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 p2, 0x0

    invoke-static {p1, p2}, Lio/peakmood/mobile/MainActivity;->access$2802(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 829
    return-void
.end method
