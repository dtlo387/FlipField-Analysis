# Automated Builds Guide

## 🤖 How Automated Builds Work

This repository uses **GitHub Actions** to automatically build executables for Windows, macOS, and Linux whenever you push code. No manual building required!

## 🚀 Triggering Builds

### **Automatic Triggers:**
- **Push to main branch**: Creates development builds
- **Create a tag**: Creates a full release with all executables
- **Pull requests**: Tests builds without releasing

### **Manual Trigger:**
- Go to **Actions** tab on GitHub
- Click **"Build Executables"** workflow
- Click **"Run workflow"** button

## 📦 Build Outputs

### **For Regular Pushes:**
Executables are created as **downloadable artifacts**:
1. Go to **Actions** tab
2. Click on the latest workflow run
3. Scroll down to **Artifacts** section
4. Download platform-specific files

### **For Tagged Releases:**
Executables are automatically added to **GitHub Releases**:
1. Create a tag: `git tag v1.2.0`
2. Push the tag: `git push origin v1.2.0`
3. GitHub automatically creates a release with all executables

## 🏷️ Creating Releases

### **Step-by-Step Release Process:**

```bash
# 1. Make sure all changes are committed and pushed
git add .
git commit -m "Ready for release v1.2.0"
git push origin main

# 2. Create and push a version tag
git tag v1.2.0
git push origin v1.2.0

# 3. GitHub Actions will automatically:
#    - Build for Windows, macOS, and Linux
#    - Create a new release
#    - Upload all executables
#    - Add release notes
```

### **Tag Naming Convention:**
- `v1.0.0` - Major release
- `v1.1.0` - Minor update
- `v1.1.1` - Bug fix

## 📋 What Gets Built

Each platform creates:

### **🐧 Linux**
- `FlipField_Analysis_Linux` - Executable binary
- Compatible with most Linux distributions

### **🪟 Windows** 
- `FlipField_Analysis_Windows.exe` - Single executable
- Compatible with Windows 7/8/10/11

### **🍎 macOS**
- `FlipField_Analysis_macOS.app` - App bundle
- Universal binary (Intel + Apple Silicon)

## ⚙️ Build Configuration

The workflow file (`.github/workflows/build-executables.yml`) handles:
- **Python 3.11** setup on all platforms
- **Dependency installation** from `requirements.txt`
- **PyInstaller** executable creation
- **Custom icon** inclusion
- **Artifact uploading**
- **Release creation** (for tags)

## 🛠️ Customizing Builds

### **To modify build settings:**
1. Edit `.github/workflows/build-executables.yml`
2. Common changes:
   - Python version: Change `python-version: '3.11'`
   - Build flags: Modify `pyinstaller` commands
   - Artifact names: Update `artifact_name` in matrix

### **To add new platforms:**
Add to the matrix in the workflow file:
```yaml
matrix:
  os: [ubuntu-latest, windows-latest, macos-latest, windows-2019]
```

## 🔍 Monitoring Builds

### **Check Build Status:**
1. Go to **Actions** tab on GitHub
2. See status of current/recent builds
3. Click on any build to see detailed logs

### **Build Failures:**
- Check the **Actions** tab for error details
- Common issues:
  - Dependency conflicts
  - Platform-specific code issues
  - Missing files

## 📊 Build Times (Approximate)

- **Linux**: ~5-8 minutes
- **Windows**: ~8-12 minutes  
- **macOS**: ~10-15 minutes
- **Total**: ~15-20 minutes for all platforms

## 💡 Tips

1. **Test locally first**: Use `build_simple.py` before pushing
2. **Tag releases carefully**: Tags trigger public releases
3. **Check logs**: If builds fail, Actions tab shows why
4. **Free tier limits**: GitHub gives ~2000 minutes/month for free
5. **Manual triggers**: Use workflow_dispatch for testing

## 🎯 Benefits

- ✅ **Cross-platform**: All three platforms built simultaneously
- ✅ **Consistent**: Same environment every time
- ✅ **Automatic**: No manual work required
- ✅ **Fast**: Parallel builds save time
- ✅ **Reliable**: GitHub's infrastructure
- ✅ **Free**: Included with public repositories

---

Your users can now get executables for any platform without needing Python! 🚀 